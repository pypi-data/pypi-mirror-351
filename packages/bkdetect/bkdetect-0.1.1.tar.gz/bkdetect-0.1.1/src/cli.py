import sys
import time
from pathlib import Path
from .core import bkDetect

def main():
    if len(sys.argv) < 3:
        print("Usage: python source_finder.py <documents_directory_or_file> <query_file>")
        sys.exit(1)

    docs_path = Path(sys.argv[1])
    query_path = Path(sys.argv[2])

    finder = bkDetect(
        input_path=docs_path,
        language="ru",
        use_cache=False
    )

    print("Индексация документов...")
    t0 = time.time()
    finder.build_index()
    print(f"Индексация завершена за {time.time() - t0:.4f} секунд\n")

    print("Похожие документы:")
    t1 = time.time()
    results = finder.find_sources_from_file(query_path)
    for path, score in results:
        print(f"{path.name} - score: {score:.4f}")
    print(f"Поиск похожих документов занял {time.time() - t1:.4f} секунд\n")

    print("Позиции вхождений:")
    t2 = time.time()
    query_text = query_path.read_text(encoding='utf-8', errors='ignore')
    positions = finder.locate_source_positions(query_text, top_k=10, max_positions_per_file=3)
    
    for path, pos_info, snippet, score, source_type in positions:
        print(f"{path.name} - {pos_info} ({source_type}): {snippet} [score: {score:.4f}]")
    
    print(f"Поиск позиций занял {time.time() - t2:.4f} секунд")
    print(f"Общее время: {time.time() - t0:.4f} секунд")
    
if __name__ == "__main__":
    main()