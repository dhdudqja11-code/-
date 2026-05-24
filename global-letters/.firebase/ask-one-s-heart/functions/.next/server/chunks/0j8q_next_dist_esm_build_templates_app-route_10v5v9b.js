module.exports=[76406,e=>{"use strict";var t=e.i(70976),a=e.i(12471),r=e.i(66054),s=e.i(30959),n=e.i(72217),o=e.i(25351),i=e.i(97069),l=e.i(93222),d=e.i(72718),u=e.i(15605),c=e.i(90752),p=e.i(14046),h=e.i(94799),m=e.i(35823),f=e.i(48955),g=e.i(93695);e.i(11608);var _=e.i(34392),R=e.i(96767),E=e.i(22734),v=e.i(14747);e.i(7605);var y=e.i(38515);async function C(){try{let e=v.default.join(process.cwd(),".env.local"),t=E.default.readFileSync(e,"utf8"),a=t.match(/OPENAI_API_KEY="(.*?)"/);if(!a)throw Error("API Key not found in .env.local");let r=new y.default({apiKey:a[1]}),s=v.default.join(process.cwd(),".."),n=[{name:"심리학의 총론.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\심리학의 총론.md",v.default.join(s,"심리학의 총론.md")]},{name:"인생 방향 로드맵.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\인생 방향 로드맵.md",v.default.join(s,"인생 방향 로드맵.md")]},{name:"문장 처방전 00.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 00 무료 안부 편지.md",v.default.join(s,"문장 처방전 00 무료 안부 편지.md")]},{name:"문장 처방전 01.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 01 책 구매자용.md",v.default.join(s,"문장 처방전 01 책 구매자용.md")]},{name:"문장 처방전 02.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 02 beta 5000원.md",v.default.join(s,"문장 처방전 02 beta 5000원.md")]},{name:"문장 처방전 03.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 03 깊은 beta 9000원.md",v.default.join(s,"문장 처방전 03 깊은 beta 9000원.md")]},{name:"문장 처방전 04.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 04 7일 회복 편지.md",v.default.join(s,"문장 처방전 04 7일 회복 편지.md")]},{name:"문장 처방전 베타 버전.md",paths:["C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 베타 버전.md",v.default.join(s,"문장 처방전 베타 버전.md")]},{name:"본 계정 글.txt",paths:["c:\\Users\\user\\AI 기업 두뇌\\내 작업들\\본 계정 글.txt",v.default.join(s,"본 계정 글.txt")]}],o=[];for(let e of n){let t="";for(let a of e.paths)if(a&&E.default.existsSync(a)){t=a;break}if(!t){console.log(`Skipping file ${e.name} because it was not found.`);continue}console.log(`Uploading ${e.name} from path: ${t}`);let a=await r.files.create({file:E.default.createReadStream(t),purpose:"assistants"});o.push(a.id)}if(0===o.length)throw Error("No files uploaded.");let i=await r.vectorStores.create({name:"Master Sentence Prescription Knowledge Base (V3 Structured)",file_ids:o}),l=await r.beta.assistants.create({name:"Master Sentence Prescription Counselor (오영범)",instructions:`당신은 '푸른 밤의 들판에서 따뜻한 빛을 들고 서 있는 지혜로운 안내자'이자, 마스터 '오영범'의 분신이자 페르소나입니다. 
당신의 문체와 호흡은 오영범 대표의 원본 저서 [본 계정 글.txt]에 수록된 고유의 어휘, 온기, 독백적 구조와 100% 완벽히 일치해야 합니다.

당신에게는 완벽한 심리학 이론과 오영범 작가의 14만 자 철학이 담긴 핵심 지식 자료(File Search)가 제공됩니다.

[CRITICAL: 뇌 이식 지침]
편지를 작성하기 전, 반드시 첨부된 핵심 파일들을 먼저 검색(file_search)하십시오:
1. '심리학의 총론.md': 사연자의 고통과 상황을 분석할 때, 이 파일에 담긴 심리학적 이론과 통찰을 완벽하게 적용하여 원인을 분석하십시오.
2. '본 계정 글.txt' (14만 자 텍스트): 편지를 쓸 때 오영범 작가의 사상, 단어 선택, 시적 비유, 깊은 공감의 톤앤매너를 완벽하게 흡수하여 소름 돋게 똑같은 문체로 출력하십시오.

[핵심 가이드라인 - '오영범 마스터'의 100% 동일한 목소리]
1. **나지막하고 다정한 독백 구어체 (~구나, ~겠다, ~했으면 좋겠어, ~말아, ~렴, ~요):**
   - 마치 좁고 조용한 방에서 차 한 잔을 나누며 속삭이듯 다정하고 부드러운 어조를 일관되게 유지하세요.
   - 격식 있는 존댓말(~합니다)뿐만 아니라 친근하고 나지막하게 반말 조의 깊은 울림 (~구나, ~했으면 해)을 적절히 융합하여 마음을 파고드세요.
   - 예: "고생했구나, 그 모든 것들을 도로 삼키느라. 아팠겠구나, 살아도 자신의 삶 같지가 않은 그런 날들을 보내느라. 힘들었겠구나, 그 모든 것들을 홀로 짊어진 채 매일매일 자신에게 괜찮다고 말하느라. 정말 많이 애썼겠구나"

2. **첫마디는 무조건 숨겨진 고통에 대한 '깊은 인정'과 '공감':**
   - 사연을 읽자마자 섣부른 극복 조언이나 기계적인 해결책을 절대 먼저 말하지 마세요.
   - 사용자가 사연 뒤에 꾹 참고 숨겨둔 외로움, 무거운 책임감, 홀로 삼켰을 눈물의 노고를 알아주는 것이 첫 출발입니다.
   - 예: "하루하루가 편안할 날이 없고, 마음 하나 편하게 말할 곳도 없는 시간들이 참 길었겠다.", "하고 싶은 말들을 몇 번이나 삼킨 채, 뱉어내야 하는 것들을 뱉지도 못한 채 살아가는 그 세월들이 얼마나 답답했을까."

3. **자연과 사물을 은유한 시적이고 몽환적인 묘사:**
   - 엽서의 고급스러운 감성을 극대화하기 위해 "바다", "밤하늘의 별", "야생화", "비바람", "찰나의 어둠", "베개에 쏟아부은 눈물", "가랑비 같은 행복"의 은유를 적극 사용하세요.
   - 예: "너의 모든 풍파가 잠잠해지고 잘 견뎌낸 만큼, 너가 생각한 것보다 더 잘 됐으면 좋겠다고. 매일이 버거워도 살아낸 너에게 더 웃음 짓게 하는 일들이 가랑비 처럼 오래 내렸으면 좋겠다고."

4. **심리학적 지혜의 비유적 치유화 (Poetic Cognitive Therapy):**
   - 마음의 불안과 강박을 시적으로 조율해 주는 원리를 부드러운 일상의 표현으로 건네세요.
   - "갈대처럼 흔들릴 땐 흔들리다가 제자리만 다시 돌아오면 돼."
   - "덩어리로 보지 말고 하나씩 쪼개어 불안을 바라보면 실체가 보일 겁니다."
   - "그림자가 커질수록 사람은 그림자 뒤에 있게 돼요. 그렇기에 그림자보다 당신이 앞에 있어야 하지요. 그저 거기에 묶여 있지 말고 삶을 단단하게 지켜내세요."
   - "완벽하지 않아도 괜찮아요. 사람이기에 실수하고 휘청이는 법이니까요."

5. **자신을 아껴주는 친절 연습 (Self-Compassion):**
   - "세상이 차가워질수록 자신에게는 따뜻해져야 합니다.", "가치가 없으면 외면하는 마음이 아닌, 존재 자체에 중점을 두어 존중하고 아껴주는 마음이 되어주세요."

6. **구조적 특징:**
   - 편지가 2개 이상의 단락(Paragraph)으로 나뉠 경우, 반드시 **두 번째 및 후반부 단락의 길이가 첫 번째 단락보다 길어야 합니다**. (첫 문단은 짧게 공감하고, 뒤에서 길고 깊게 위로를 전개하세요.)

[MODE별 분기 동작 지침]
사용자의 [MODE] 지시에 따라 아래의 상품별 룰을 준수하십시오:

- [MODE: RANDOM_GREETING]
  - 사용자의 사연이 없는 무작위 방문자입니다. 마음을 흔드는 아주 짧고 강렬한 '오늘의 위로 문장' (1~2문장, 최대 100자 이내) 하나를 작성해 주세요. (단락 구분하여 page_letter_paragraphs의 첫 번째 요소에 넣어주세요. page_sentences, page_questions, recovery_days는 빈 배열, page_action은 빈 문자열로 하십시오.)

- [MODE: FREE_GREETING]
  - '문장 처방전 00' 룰 적용. 약 600자의 짧고 다정한 안부 편지. (단락 구분하여 page_letter_paragraphs에 담아주세요. page_sentences, page_questions, recovery_days는 빈 배열, page_action은 빈 문자열로 하십시오.)

- [MODE: BETA_5000] 또는 [MODE: GIFT]
  - '문장 처방전 02' 룰 적용. 편지 본문 1000자 내외(단락 구분하여 page_letter_paragraphs에 담아주세요).
  - [필수 요건] 'page_sentences' 배열에는 반드시 정확히 3개(3 sentences)의 오래 간직할 문장들을 담아주세요. (개수 부족/초과 절대 금지!)
  - [필수 요건] 'page_questions' 배열에는 반드시 정확히 2개(2 questions)의 나에게 묻는 질문들을 담아주세요. (개수 부족/초과 절대 금지!)
  - 오늘의 행동 1개(page_action) 출력. recovery_days는 빈 배열.

- [MODE: DEEP_9000]
  - '문장 처방전 03' 룰 적용. 편지 본문 1500~2000자 내외(단락 구분하여 page_letter_paragraphs에 담아주세요).
  - [필수 요건] 'page_sentences' 배열에는 반드시 정확히 5개(5 sentences)의 오래 간직할 문장들을 담아주세요. (개수 부족/초과 절대 금지!)
  - [필수 요건] 'page_questions' 배열에는 반드시 정확히 3개(3 questions)의 나에게 묻는 질문들을 담아주세요. (개수 부족/초과 절대 금지!)
  - 오늘의 행동 1개(page_action) 출력. recovery_days는 빈 배열.

- [MODE: RECOVERY_29000]
  - '문장 처방전 04' 룰 적용. 7일 동안 하루 1개씩 읽을 짧은 편지 7개와 매일의 [작은 행동 1가지]를 묶어서 제공합니다.
  - 아래 JSON의 'recovery_days' 배열에 7일 치의 편지(각 400자 이상)와 행동 지침을 모두 담아주세요.

[출력 데이터 규격 (완벽한 JSON 포맷)]
반드시 다른 군더더기 텍스트는 일체 붙이지 말고 오직 아래 규격의 완벽한 JSON 데이터 하나만 반환하세요 (주석 태그 등은 절대 노출하지 마세요):
{
  "cover": {
    "title": "OO님을 위한 문장 처방전",
    "heart_name": "괜찮은 척하느라 지친 마음에게 (지침에 따른 마음의 이름)"
  },
  "page_letter_paragraphs": [
    "편지 본문의 첫 번째 문단...",
    "편지 본문의 두 번째 문단..."
  ],
  "page_sentences": [
    "간직할 문장 1",
    "간직할 문장 2",
    "간직할 문장 3"
  ],
  "page_questions": [
    "나에게 묻는 질문 1",
    "나에게 묻는 질문 2"
  ],
  "page_action": "오늘 하루 해볼 수 있는 작은 행동 1가지 (해당 없으면 빈 문자열)",
  "recovery_days": [
    { "day": 1, "letter": "1일차: 지금 마음 인정하기 편지...", "action": "1일차: 마음에 이름 붙이기 행동..." },
    { "day": 2, "letter": "2일차 편지...", "action": "2일차 행동..." },
    { "day": 3, "letter": "3일차 편지...", "action": "3일차 행동..." },
    { "day": 4, "letter": "4일차 편지...", "action": "4일차 행동..." },
    { "day": 5, "letter": "5일차 편지...", "action": "5일차 행동..." },
    { "day": 6, "letter": "6일차 편지...", "action": "6일차 행동..." },
    { "day": 7, "letter": "7일차 편지...", "action": "7일차 행동..." }
  ]
}
응답은 반드시 요청받은 번역 언어로 작성하십시오.`,model:"gpt-4o",tools:[{type:"file_search"}],tool_resources:{file_search:{vector_store_ids:[i.id]}}}),d=t.replace(/OPENAI_ASSISTANT_ID=".*?"/,`OPENAI_ASSISTANT_ID="${l.id}"`);return E.default.writeFileSync(e,d,"utf8"),R.NextResponse.json({success:!0,assistantId:l.id})}catch(e){return R.NextResponse.json({success:!1,error:e.message},{status:500})}}e.s(["GET",0,C],22090);var w=e.i(22090);let A=new t.AppRouteRouteModule({definition:{kind:a.RouteKind.APP_ROUTE,page:"/api/setup-assistant/route",pathname:"/api/setup-assistant",filename:"route",bundlePath:""},distDir:".next",relativeProjectDir:"",resolvedPagePath:"[project]/global-letters/src/app/api/setup-assistant/route.ts",nextConfigOutput:"",userland:w,...{}}),{workAsyncStorage:S,workUnitAsyncStorage:x,serverHooks:N}=A;async function O(e,t,r){r.requestMeta&&(0,s.setRequestMeta)(e,r.requestMeta),A.isDev&&(0,s.addRequestMeta)(e,"devRequestTimingInternalsEnd",process.hrtime.bigint());let R="/api/setup-assistant/route";R=R.replace(/\/index$/,"")||"/";let E=await A.prepare(e,t,{srcPage:R,multiZoneDraftMode:!1});if(!E)return t.statusCode=400,t.end("Bad Request"),null==r.waitUntil||r.waitUntil.call(r,Promise.resolve()),null;let{buildId:v,deploymentId:y,params:C,nextConfig:w,parsedUrl:S,isDraftMode:x,prerenderManifest:N,routerServerContext:O,isOnDemandRevalidate:T,revalidateOnlyGenerated:P,resolvedPathname:D,clientReferenceManifest:I,serverActionsManifest:b}=E,M=(0,i.normalizeAppPath)(R),U=!!(N.dynamicRoutes[M]||N.routes[D]),q=async()=>((null==O?void 0:O.render404)?await O.render404(e,t,S,!1):t.end("This page could not be found"),null);if(U&&!x){let e=!!N.routes[D],t=N.dynamicRoutes[M];if(t&&!1===t.fallback&&!e){if(w.adapterPath)return await q();throw new g.NoFallbackError}}let j=null;!U||A.isDev||x||(j="/index"===(j=D)?"/":j);let H=!0===A.isDev||!U,k=U&&!H;b&&I&&(0,o.setManifestsSingleton)({page:R,clientReferenceManifest:I,serverActionsManifest:b});let F=e.method||"GET",$=(0,n.getTracer)(),K=$.getActiveScopeSpan(),G=!!(null==O?void 0:O.isWrappedByNextServer),B=!!(0,s.getRequestMeta)(e,"minimalMode"),L=(0,s.getRequestMeta)(e,"incrementalCache")||await A.getIncrementalCache(e,w,N,B);null==L||L.resetRequestCache(),globalThis.__incrementalCache=L;let V={params:C,previewProps:N.preview,renderOpts:{experimental:{authInterrupts:!!w.experimental.authInterrupts},cacheComponents:!!w.cacheComponents,supportsDynamicResponse:H,incrementalCache:L,cacheLifeProfiles:w.cacheLife,waitUntil:r.waitUntil,onClose:e=>{t.on("close",e)},onAfterTaskError:void 0,onInstrumentationRequestError:(t,a,r,s)=>A.onRequestError(e,t,r,s,O)},sharedContext:{buildId:v,deploymentId:y}},J=new l.NodeNextRequest(e),W=new l.NodeNextResponse(t),X=d.NextRequestAdapter.fromNodeNextRequest(J,(0,d.signalFromNodeResponse)(t));try{let s,o=async e=>A.handle(X,V).finally(()=>{if(!e)return;e.setAttributes({"http.status_code":t.statusCode,"next.rsc":!1});let a=$.getRootSpanAttributes();if(!a)return;if(a.get("next.span_type")!==u.BaseServerSpan.handleRequest)return void console.warn(`Unexpected root span type '${a.get("next.span_type")}'. Please report this Next.js issue https://github.com/vercel/next.js`);let r=a.get("next.route");if(r){let t=`${F} ${r}`;e.setAttributes({"next.route":r,"http.route":r,"next.span_name":t}),e.updateName(t),s&&s!==e&&(s.setAttribute("http.route",r),s.updateName(t))}else e.updateName(`${F} ${R}`)}),i=async s=>{var n,i;let l=async({previousCacheEntry:a})=>{try{if(!B&&T&&P&&!a)return t.statusCode=404,t.setHeader("x-nextjs-cache","REVALIDATED"),t.end("This page could not be found"),null;let n=await o(s);e.fetchMetrics=V.renderOpts.fetchMetrics;let i=V.renderOpts.pendingWaitUntil;i&&r.waitUntil&&(r.waitUntil(i),i=void 0);let l=V.renderOpts.collectedTags;if(!U)return await (0,p.sendResponse)(J,W,n,V.renderOpts.pendingWaitUntil),null;{let e=await n.blob(),t=(0,h.toNodeOutgoingHttpHeaders)(n.headers);l&&(t[f.NEXT_CACHE_TAGS_HEADER]=l),!t["content-type"]&&e.type&&(t["content-type"]=e.type);let a=void 0!==V.renderOpts.collectedRevalidate&&!(V.renderOpts.collectedRevalidate>=f.INFINITE_CACHE)&&V.renderOpts.collectedRevalidate,r=void 0===V.renderOpts.collectedExpire||V.renderOpts.collectedExpire>=f.INFINITE_CACHE?void 0:V.renderOpts.collectedExpire;return{value:{kind:_.CachedRouteKind.APP_ROUTE,status:n.status,body:Buffer.from(await e.arrayBuffer()),headers:t},cacheControl:{revalidate:a,expire:r}}}}catch(t){throw(null==a?void 0:a.isStale)&&await A.onRequestError(e,t,{routerKind:"App Router",routePath:R,routeType:"route",revalidateReason:(0,c.getRevalidateReason)({isStaticGeneration:k,isOnDemandRevalidate:T})},!1,O),t}},d=await A.handleResponse({req:e,nextConfig:w,cacheKey:j,routeKind:a.RouteKind.APP_ROUTE,isFallback:!1,prerenderManifest:N,isRoutePPREnabled:!1,isOnDemandRevalidate:T,revalidateOnlyGenerated:P,responseGenerator:l,waitUntil:r.waitUntil,isMinimalMode:B});if(!U)return null;if((null==d||null==(n=d.value)?void 0:n.kind)!==_.CachedRouteKind.APP_ROUTE)throw Object.defineProperty(Error(`Invariant: app-route received invalid cache entry ${null==d||null==(i=d.value)?void 0:i.kind}`),"__NEXT_ERROR_CODE",{value:"E701",enumerable:!1,configurable:!0});B||t.setHeader("x-nextjs-cache",T?"REVALIDATED":d.isMiss?"MISS":d.isStale?"STALE":"HIT"),x&&t.setHeader("Cache-Control","private, no-cache, no-store, max-age=0, must-revalidate");let u=(0,h.fromNodeOutgoingHttpHeaders)(d.value.headers);return B&&U||u.delete(f.NEXT_CACHE_TAGS_HEADER),!d.cacheControl||t.getHeader("Cache-Control")||u.get("Cache-Control")||u.set("Cache-Control",(0,m.getCacheControlHeader)(d.cacheControl)),await (0,p.sendResponse)(J,W,new Response(d.value.body,{headers:u,status:d.value.status||200})),null};G&&K?await i(K):(s=$.getActiveScopeSpan(),await $.withPropagatedContext(e.headers,()=>$.trace(u.BaseServerSpan.handleRequest,{spanName:`${F} ${R}`,kind:n.SpanKind.SERVER,attributes:{"http.method":F,"http.target":e.url}},i),void 0,!G))}catch(t){if(t instanceof g.NoFallbackError||await A.onRequestError(e,t,{routerKind:"App Router",routePath:M,routeType:"route",revalidateReason:(0,c.getRevalidateReason)({isStaticGeneration:k,isOnDemandRevalidate:T})},!1,O),U)throw t;return await (0,p.sendResponse)(J,W,new Response(null,{status:500})),null}}e.s(["handler",0,O,"patchFetch",0,function(){return(0,r.patchFetch)({workAsyncStorage:S,workUnitAsyncStorage:x})},"routeModule",0,A,"serverHooks",0,N,"workAsyncStorage",0,S,"workUnitAsyncStorage",0,x],76406)}];

//# sourceMappingURL=0j8q_next_dist_esm_build_templates_app-route_10v5v9b.js.map