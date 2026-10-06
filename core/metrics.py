"""[Giai đoạn 1] Chỉ số tính bằng code, đưa vào prompt để LLM nhận xét dựa trên số liệu thật:
số từ, độ dài câu TB, tỉ lệ câu đơn/phức, từ lặp lại, độ đa dạng từ vựng (TTR),
tỉ lệ từ theo mức CEFR (cần data/wordlists/ — chưa có). Viết unit test trong tests/.
"""
import re
from collections import Counter

# Từ nối báo hiệu câu phức (heuristic — đủ để so sánh tương đối giữa các bài, không phải parser ngữ pháp)
SUBORDINATORS = {"because", "although", "though", "which", "who", "whom", "whose", "where", "when", "while",
                 "whereas", "if", "unless", "since", "that", "until", "whether", "once", "as"}
STOPWORDS = {"the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with", "at", "by", "from", "as",
             "is", "are", "was", "were", "be", "been", "being", "it", "its", "this", "that", "these", "those",
             "they", "them", "their", "he", "she", "his", "her", "we", "our", "you", "your", "i", "my", "me",
             "not", "can", "will", "would", "should", "could", "may", "might", "must", "do", "does", "did",
             "have", "has", "had", "more", "most", "so", "than", "also", "which", "who", "what", "there", "if",
             "because", "when", "while", "some", "many", "other", "such", "very", "all", "one", "people"}
_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.splitlines() if p.strip()]


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if _WORD.search(s)]


def words(text: str) -> list[str]:
    return [w.lower().replace("’", "'") for w in _WORD.findall(text)]


def is_complex(sentence: str) -> bool:
    return any(w in SUBORDINATORS for w in words(sentence))


def compute(essay: str) -> dict:
    """Trả dict chỉ số. cefr_profile = None cho tới khi có data/wordlists/."""
    ws, ss = words(essay), sentences(essay)
    content = [w for w in ws if w not in STOPWORDS and len(w) > 2]
    complex_n = sum(is_complex(s) for s in ss)
    return {
        "word_count": len(ws),
        "sentence_count": len(ss),
        "paragraph_count": len(paragraphs(essay)),
        "avg_sentence_len": round(len(ws) / len(ss), 1) if ss else 0.0,
        "complex_sentence_ratio": round(complex_n / len(ss), 2) if ss else 0.0,
        # TTR phụ thuộc độ dài bài → chỉ so sánh giữa các bài có độ dài gần nhau
        "type_token_ratio": round(len(set(ws)) / len(ws), 2) if ws else 0.0,
        "repeated_words": [w for w, n in Counter(content).most_common(8) if n >= 3],
        "cefr_profile": None,
    }


def to_prompt_block(m: dict) -> str:
    """Định dạng chỉ số để chèn vào prompt."""
    lines = [f"- {k}: {v}" for k, v in m.items() if v is not None]
    return "<metrics>\n" + "\n".join(lines) + "\n</metrics>"
