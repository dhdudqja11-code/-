import { NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: Request) {
  try {
    const { story, productType } = await req.json();

    // 2026년 차세대 Responses API를 활용한 스트리밍 없는 즉시 렌더링 방식 백업 코드
    const completion = await openai.chat.completions.create({
      model: "gpt-4o", // 향후 gpt-5 등 교체
      messages: [
        {
          role: "system",
          content: "당신은 세계 최고의 심리 상담사 오영범 마스터입니다. 다정하고 따뜻한 위로 편지를 작성하여 완벽한 다중 페이지 JSON 포맷으로 응답하세요."
        },
        {
          role: "user",
          content: `사용자의 사연입니다: ${story}\n요금제(${productType})에 맞게 JSON을 생성해주세요.`
        }
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
      max_tokens: 2000,
    });

    const finalJsonString = completion.choices[0].message.content || "{}";
    const parsedData = JSON.parse(finalJsonString);

    return NextResponse.json(parsedData);
  } catch (error: any) {
    console.error("차세대 API 통신 에러:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
