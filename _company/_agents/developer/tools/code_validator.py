#!/usr/bin/env python3
import sys
import os
import io
import ast
import json
import builtins
import argparse

# Windows cp949 인코딩으로 인한 문자 출력 에러 방지 (강제 UTF-8 설정)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class PythonSyntaxValidator:
    def __init__(self, code, filename="<string>"):
        self.code = code
        self.filename = filename
        self.errors = []
        self.warnings = []

    def validate(self):
        # 1. 기본적인 AST 파싱 (Syntax Error 검증)
        try:
            tree = ast.parse(self.code, filename=self.filename)
        except SyntaxError as e:
            self.errors.append({
                "type": "SyntaxError",
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text.strip() if e.text else ""
            })
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append({
                "type": "ParsingError",
                "message": f"AST 파싱 중 예기치 않은 오류가 발생했습니다: {str(e)}",
                "line": 1,
                "offset": 0,
                "text": ""
            })
            return False, self.errors, self.warnings

        # 2. 임포트 누락 및 정의되지 않은 이름 검증 (NameError 정적 분석)
        self.check_name_errors(tree)
        
        # 에러가 있으면 False, 없으면 True
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def check_name_errors(self, tree):
        # 1단계: 내장 함수/클래스 목록 가져오기
        builtin_names = set(dir(builtins))
        
        # 2단계: 코드 내에서 바인딩(정의)되는 이름들 찾기
        bound_names = set()
        
        # 전역/로컬 바인딩 추적을 위한 심플한 수집기
        class BoundNameCollector(ast.NodeVisitor):
            def __init__(self):
                self.names = set()
                self.in_function = False
                
            def visit_Import(self, node):
                for alias in node.names:
                    # 'import os' -> 'os', 'import numpy as np' -> 'np'
                    self.names.add(alias.asname if alias.asname else alias.name.split('.')[0])
                self.generic_visit(node)
                
            def visit_ImportFrom(self, node):
                for alias in node.names:
                    # 'from datetime import timedelta' -> 'timedelta'
                    self.names.add(alias.asname if alias.asname else alias.name)
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                self.names.add(node.name)
                # 함수 내부 바인딩은 단순화하기 위해 함수 내부에서 정의된 변수와 인자도 수집
                # 정밀한 스코프 분석이 아닌 '누락 임포트 감지'가 목적이므로 전체 스코프에서 바인딩된 이름을 합집합 처리
                for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                    self.names.add(arg.arg)
                if node.args.vararg:
                    self.names.add(node.args.vararg.arg)
                if node.args.kwarg:
                    self.names.add(node.args.kwarg.arg)
                self.generic_visit(node)
                
            def visit_AsyncFunctionDef(self, node):
                self.names.add(node.name)
                for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                    self.names.add(arg.arg)
                if node.args.vararg:
                    self.names.add(node.args.vararg.arg)
                if node.args.kwarg:
                    self.names.add(node.args.kwarg.arg)
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.names.add(node.name)
                self.generic_visit(node)
                
            def visit_Assign(self, node):
                # 'a = 10' -> 'a'
                for target in node.targets:
                    self.collect_target_names(target)
                self.generic_visit(node)
                
            def visit_AnnAssign(self, node):
                # 'a: int = 10' -> 'a'
                self.collect_target_names(node.target)
                self.generic_visit(node)
                
            def visit_For(self, node):
                # 'for i in range(10)' -> 'i'
                self.collect_target_names(node.target)
                self.generic_visit(node)
                
            def visit_withitem(self, node):
                if node.optional_vars:
                    self.collect_target_names(node.optional_vars)
                    
            def collect_target_names(self, target):
                if isinstance(target, ast.Name):
                    self.names.add(target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for elt in target.elts:
                        self.collect_target_names(elt)

        collector = BoundNameCollector()
        collector.visit(tree)
        bound_names.update(collector.names)
        
        # 3단계: 사용되는 이름(ast.Name) 중 정의되지 않은 이름 검출
        class UsedNameVisitor(ast.NodeVisitor):
            def __init__(self):
                self.used = []
                
            def visit_Name(self, node):
                # Load 컨텍스트로 사용되는 이름만 수집 (정의하는 Store나 삭제하는 Del은 제외)
                if isinstance(node.ctx, ast.Load):
                    self.used.append((node.id, node.lineno, node.col_offset))
                self.generic_visit(node)
                
        visitor = UsedNameVisitor()
        visitor.visit(tree)
        
        # 대표적인 누락 임포트 대응 가이드 딕셔너리
        import_suggestions = {
            "timedelta": "from datetime import timedelta",
            "datetime": "from datetime import datetime",
            "time": "import time",
            "json": "import json",
            "sys": "import sys",
            "os": "import os",
            "pytest": "import pytest",
            "FastAPI": "from fastapi import FastAPI",
            "Depends": "from fastapi import Depends",
            "HTTPException": "from fastapi import HTTPException",
            "status": "from fastapi import status",
            "APIRouter": "from fastapi import APIRouter",
            "BaseModel": "from pydantic import BaseModel",
            "UUID": "from uuid import UUID",
            "uuid4": "from uuid import uuid4",
            "bcrypt": "import bcrypt",
            "Signer": "from itsdangerous import Signer",
            "BadSignature": "from itsdangerous import BadSignature"
        }
        
        seen_unresolved = set()
        for name, lineno, col in visitor.used:
            # 내장 객체도 아니고, 바인딩된 이름도 아니라면 NameError 위험
            if name not in builtin_names and name not in bound_names:
                if name in seen_unresolved:
                    continue
                seen_unresolved.add(name)
                
                # 가이드 메시지 작성
                suggestion = import_suggestions.get(name)
                if suggestion:
                    msg = f"NameError: name '{name}' is not defined. Please import with '{suggestion}'."
                else:
                    msg = f"NameError: name '{name}' is not defined. Please import or define this variable."
                
                self.errors.append({
                    "type": "NameError",
                    "message": msg,
                    "line": lineno,
                    "offset": col,
                    "text": name
                })

def main():
    parser = argparse.ArgumentParser(description="AI 1인 기업 파이썬 문법 및 임포트 검증기")
    parser.add_argument("--file", required=True, help="분석할 소스 파일 경로")
    parser.add_argument("--content-file", required=True, help="검증할 실제 코드가 담긴 임시 파일 경로")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.content_file):
        print(json.dumps({
            "status": "error",
            "error_type": "ValidationError",
            "message": f"콘텐츠 임시 파일을 찾을 수 없습니다: {args.content_file}",
            "errors": [],
            "warnings": []
        }, ensure_ascii=False))
        sys.exit(1)
        
    try:
        with open(args.content_file, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error_type": "ValidationError",
            "message": f"임시 파일을 읽지 못했습니다: {str(e)}",
            "errors": [],
            "warnings": []
        }, ensure_ascii=False))
        sys.exit(1)

    validator = PythonSyntaxValidator(code, filename=args.file)
    is_valid, errors, warnings = validator.validate()
    
    result = {
        "status": "ok" if is_valid else "error",
        "error_type": errors[0]["type"] if errors else None,
        "message": errors[0]["message"] if errors else "문법 및 정적 분석 검증 성공",
        "errors": errors,
        "warnings": warnings
    }
    
    # 결과를 표준 출력에 JSON으로 인쇄
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if not is_valid:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
