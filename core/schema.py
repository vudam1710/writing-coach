"""[Giai đoạn 1 — làm ĐẦU TIÊN] Cấu trúc kết quả bằng Pydantic = "hợp đồng" giữa LLM và giao diện.

Bám theo docs/design_v0.3.md mục 5–7:
- Summary: 1 câu nhận xét chung + 1–2 điều nên tập trung trước
- 4 Aspect (ideas, organization, vocabulary, grammar), mỗi aspect:
    strength (1 câu ghi nhận) + issues: tối đa 4 Issue
- Issue: title, severity (high/medium/low), ease (easy/medium/hard), quotes[],
    why_vi, learn_vi (+ cefr), rewrite (ĐÚNG 1 câu), self_practice_vi
- Level: vocab_cefr, grammar_cefr
- IELTS: band từng tiêu chí + overall + next_step (chỉ ở chế độ IELTS)
- Expand perspectives (cuối aspect 1): 2–3 dòng dàn ý
Xếp hạng issue (đã chốt): severity trước, cùng severity thì dễ sửa hơn đứng trước.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------- kiểu dữ liệu dùng chung
# Quy ước tên trường: *_vi = viết tiếng Việt, *_en = giữ tiếng Anh (để lớp 1 kiểm tra quy tắc song ngữ).
Severity = Literal["high", "medium", "low"]
Ease = Literal["easy", "medium", "hard"]
CEFR = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
AspectId = Literal["ideas", "organization", "vocabulary", "grammar"]

MAX_ISSUES = 4                      # giới hạn TRÊN, không phải chỉ tiêu (design mục 5)
VALID_BANDS = [x / 2 for x in range(0, 19)]
_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_EASE_ORDER = {"easy": 0, "medium": 1, "hard": 2}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")   # LLM thêm trường lạ → báo lỗi, không lặng lẽ bỏ qua


# ---------------------------------------------------------------- 1 vấn đề (design mục 6)
class Rewrite(_Strict):
    original_en: str = Field(description="Câu gốc trích nguyên văn từ bài")
    improved_en: str = Field(description="ĐÚNG 1 câu viết lại, ở mức i+1")


class Issue(_Strict):
    title_vi: str
    severity: Severity
    ease: Ease
    quotes_en: list[str] = Field(min_length=1, description="Trích nguyên văn từ bài")
    why_vi: str
    learn_vi: str = Field(description="Tên kiến thức cần học; thuật ngữ: 'tiếng Việt (English)'")
    learn_cefr: CEFR | None = None
    rewrite: Rewrite
    self_practice_vi: str = Field(description="Chỗ khác trong bài người học tự áp dụng")


def rank_issues(issues: list[Issue]) -> list[Issue]:
    """Đã chốt: mức độ nghiêm trọng trước; cùng mức thì vấn đề dễ sửa hơn đứng trước."""
    return sorted(issues, key=lambda i: (_SEVERITY_ORDER[i.severity], _EASE_ORDER[i.ease]))


# ---------------------------------------------------------------- 1 khía cạnh
class Aspect(_Strict):
    strength_vi: str = Field(description="1 câu ghi nhận điểm làm tốt, cụ thể")
    issues: list[Issue] = Field(default_factory=list, max_length=MAX_ISSUES)

    @model_validator(mode="after")
    def _sort(self):
        self.issues = rank_issues(self.issues)   # không tin thứ tự LLM trả về → code tự xếp
        return self


class ParagraphNote(_Strict):
    paragraph: int = Field(ge=1)
    developed: bool = Field(description="True = đoạn đã phát triển ý đầy đủ")
    note_vi: str


class Perspective(_Strict):
    angle_vi: str = Field(description="Góc nhìn: cá nhân / xã hội / kinh tế / chính phủ / ngắn-dài hạn...")
    outline_en: str = Field(description="1 dòng ý chính, dạng dàn ý, mức i+1")


class IdeasAspect(Aspect):
    """Khía cạnh 1 có thêm: nhận xét theo từng đoạn + mục 'Mở rộng góc nhìn' (cho bài sau)."""
    paragraph_notes: list[ParagraphNote] = Field(default_factory=list)
    perspectives: list[Perspective] = Field(default_factory=list, max_length=3)


# ---------------------------------------------------------------- tổng hợp, trình độ, band
class Summary(_Strict):
    overall_vi: str = Field(description="1 câu nhận xét chung")
    focus_first_vi: list[str] = Field(min_length=1, max_length=2)


class Level(_Strict):
    vocab_cefr: CEFR
    grammar_cefr: CEFR


class IeltsBands(_Strict):
    """Chỉ band từng tiêu chí do LLM cho. Overall + cap TR (<250 từ) tính bằng code (core/band.py)."""
    TR: float
    CC: float
    LR: float
    GRA: float
    next_step_vi: str = Field(description="Cần làm gì để lên band kế tiếp ở tiêu chí thấp nhất")

    @field_validator("TR", "CC", "LR", "GRA")
    @classmethod
    def _valid_band(cls, v: float) -> float:
        if v not in VALID_BANDS:
            raise ValueError(f"band {v} không hợp lệ (phải là 0.0, 0.5, ..., 9.0)")
        return v


# ---------------------------------------------------------------- kết quả cuối
class Feedback(_Strict):
    summary: Summary
    level: Level
    ideas: IdeasAspect
    organization: Aspect
    vocabulary: Aspect
    grammar: Aspect
    ielts: IeltsBands | None = None   # chỉ có ở chế độ IELTS

    def aspects(self) -> dict[str, Aspect]:
        return {"ideas": self.ideas, "organization": self.organization,
                "vocabulary": self.vocabulary, "grammar": self.grammar}


def tool_schema() -> dict:
    """JSON schema đưa vào core/llm.call_tool. (Kiểm tra lại khi làm analyzer: API có nhận $defs/$ref không.)"""
    return Feedback.model_json_schema()
