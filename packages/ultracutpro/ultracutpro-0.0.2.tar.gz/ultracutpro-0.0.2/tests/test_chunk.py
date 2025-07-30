import csv
import os
from loguru import logger
import json


class TextChunker:
    def __init__(self, csv_path, chunk_size=80, overlap=20):
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.content = []

    def process_json(self, input_file):
        "read json, get the visual part info, as csv format"
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_rag.csv"
        logger.info(f"processing json: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.id_to_timestamp_visual = {}
        for idx, row in enumerate(data):
            start_time_ms = row["start_ms"]
            end_time_ms = row["end_ms"]
            self.id_to_timestamp_visual[idx] = [start_time_ms, end_time_ms]
        # if os.path.exists(output_file):
        #     return output_file
        # else:
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            for idx, item in enumerate(data):
                line = item["description"].replace("\n", "  ")
                writer.writerow([f"{idx}. {line}"])
        logger.info(f"visual csv file: {output_file} saved.")
        return output_file

    def read_csv(self):
        if self.csv_path.endswith("json"):
            print("solving path")
            self.csv_path = self.process_json(self.csv_path)
        try:
            with open(self.csv_path, "r", encoding="utf-8") as file:
                import csv

                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row:
                        self.content.append(row[0])
            return self.content
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            return None

    def _create_chunks(self, content):
        chunks = []
        current_chunk = ""
        print(content[:30])
        for line in content:
            if ". " not in line:
                continue

            line_number, text = line.split(". ", 1)

            # 如果当前行加入会超过chunk_size
            if len(current_chunk) + len(line) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                # 处理长文本
                remaining_text = text
                while len(remaining_text) > self.chunk_size:
                    chunk_text = remaining_text[: self.chunk_size]
                    remaining_text = remaining_text[self.chunk_size :]
                    chunks.append(f"{line_number}. {chunk_text}")

                if remaining_text:
                    current_chunk = f"{line_number}. {remaining_text}"
            else:
                # 如果是chunk的第一行或可以添加到当前chunk
                if current_chunk:
                    current_chunk += f" {line_number}. {text}"
                else:
                    current_chunk = f"{line_number}. {text}"

        if current_chunk:
            chunks.append(current_chunk)

        # 处理overlap
        final_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                # 从前一个chunk获取overlap部分
                prev_chunk = chunks[i - 1]
                last_part = prev_chunk[-self.overlap :]
                # 确保overlap部分也包含行号
                if ". " in last_part:
                    final_chunks.append(last_part + " " + chunk)
                else:
                    line_num = prev_chunk.split(". ")[0]
                    final_chunks.append(f"{line_num}. {last_part} " + chunk)
            else:
                final_chunks.append(chunk)

        return final_chunks

    def process(self):
        content = self.read_csv()
        print("ddd")
        if content:
            return self._create_chunks(content)
        return None

    def save_chunks(self, output_path):
        chunks = self.process()
        # print(chunks)
        if chunks:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    for chunk in chunks:
                        f.write(chunk + "\n")
                return True
            except Exception as e:
                print(f"Error saving chunks: {str(e)}")
                return False
        return False


if __name__ == "__main__":
    a = "temp/vis_info/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200_info_visual.json"
    chunker = TextChunker(a, chunk_size=130, overlap=30)
    chunker.save_chunks(os.path.join(os.path.dirname(a), "a.txt"))
