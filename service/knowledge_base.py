import logging
import re
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)

# frozen=True 表示对象创建后不应该再改，注解 dataclass 相当于手写了一个 __init__ 方法
@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    title: str
    content: str


@dataclass(frozen=True)
class KnowledgeSearchResult:
    source: str
    title: str
    content: str
    score: int


class FileKnowledgeBase:
    # __init__ 方法会在“创建类的实例对象时”自动执行
    def __init__(self, knowledge_dir: Path | None = None) -> None:
        self.knowledge_dir = knowledge_dir or Path(__file__).resolve().parent.parent / "knowledge"

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeSearchResult]:
        # 去掉字符串前后的空格
        query = query.strip()
        if not query:
            return []
        # 从查询文本中提取关键词
        terms = self._extract_terms(query)
        results: list[KnowledgeSearchResult] = []
        # 遍历知识库的切片
        for chunk in self._load_chunks():
            # 根据关键词计算知识库切片的分数
            score = self._score_chunk(query, terms, chunk)
            if score > 0:
                results.append(
                    KnowledgeSearchResult(
                        source=chunk.source,
                        title=chunk.title,
                        content=chunk.content,
                        score=score,
                    )
                )
        # lambda item: item.score 可以理解成一个临时小函数，等价于：
        # def get_score(item):
        #     return item.score
        # 所以这行也可以写成：results.sort(key=get_score, reverse=True)
        # reverse=True 表示倒序排序
        results.sort(key=lambda item: item.score, reverse=True)
        logger.info("Knowledge search finished: query_length=%s result_count=%s", len(query), len(results))
        return results[:top_k]

    def build_context(self, query: str, top_k: int = 3) -> str:
        results = self.search(query, top_k=top_k)
        # None
        # False
        # 数字 0
        # 空字符串 ""
        # 空列表 []
        # 空字典 {}
        # 空元组 ()
        # 空集合 set()
        # results 为以上情况时这个 if 语句为判断为 true
        if not results:
            return "没有检索到相关知识库内容。"

        blocks = []
        # enumerate 是 Python 原生函数，用来“遍历列表时，同时拿到序号和值”
        for index, result in enumerate(results, start=1):
            blocks.append(
                # join 的作用是：把一个字符串列表，拼接成一个大字符串。
                # 这里的 "\n" 是“换行符”，所以：
                # "\n".join(["A", "B", "C"]) 的结果是
                # A
                # B
                # C
                # 等价于 "A" + "\n" + "B" + "\n" + "C"
                "\n".join(
                    [
                        # 字符串前面的 f 表示这是一个“格式化字符串”。允许在字符串中使用变量
                        f"[知识片段 {index}]",
                        f"来源：{result.source}",
                        f"标题：{result.title}",
                        result.content,
                    ]
                )
            )
        return "\n\n".join(blocks)

    def _load_chunks(self) -> list[KnowledgeChunk]:
        if not self.knowledge_dir.exists():
            logger.warning("Knowledge directory does not exist: %s", self.knowledge_dir)
            return []

        chunks: list[KnowledgeChunk] = []
        # glob 是 Path 对象的方法，用来按规则查找文件
        for path in sorted(self.knowledge_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            # extend 是“把另一个可遍历对象里的元素逐个加进去”。
            chunks.extend(self._split_markdown(path.name, text))
        return chunks

    def _split_markdown(self, source: str, text: str) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        # 把 source 当成一个文件路径，然后取它的“文件名主体”，不包含后缀名。
        title = Path(source).stem
        lines: list[str] = []

        def flush() -> None:
            # line.strip() 会去掉字符串前后的空格、换行、制表符。
            content = "\n".join(line for line in lines if line.strip()).strip()
            if content:
                # append 是“把整个对象作为一个元素加进去”
                chunks.append(KnowledgeChunk(source=source, title=title, content=content))

        # splitlines 返回字符串中所有行的列表，并在行边界处换行。
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                flush()
                # group(2) 的意思是：取正则表达式里第 2 个括号匹配到的内容
                title = heading.group(2).strip()
                lines = [line]
                continue
            lines.append(line)

        flush()
        return chunks

    def _extract_terms(self, query: str) -> set[str]:
        normalized_query = query.lower()
        # re.findall 是正则查找函数，会返回所有匹配到的内容，然后 set(["items", "price", "items"]) 自动去重。
        terms = set(re.findall(r"[a-z0-9_]+", normalized_query))

        chinese_parts = re.findall(r"[\u4e00-\u9fff]+", query)
        for part in chinese_parts:
            if len(part) <= 4:
                terms.add(part)
                continue
            for index in range(len(part) - 1):
                terms.add(part[index : index + 2])

        return {term for term in terms if len(term) >= 2}

    def _score_chunk(self, query: str, terms: set[str], chunk: KnowledgeChunk) -> int:
        haystack = f"{chunk.title}\n{chunk.content}".lower()
        normalized_query = query.lower()
        score = 0

        if normalized_query and normalized_query in haystack:
            score += len(normalized_query) * 2

        for term in terms:
            # 统计 term 在 haystack 中出现了几次
            count = haystack.count(term.lower())
            if count:
                score += count * len(term)

        return score


knowledge_base = FileKnowledgeBase()
