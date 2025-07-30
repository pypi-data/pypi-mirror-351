import csv
import json
from ultracutpro.rag.embed import RAGSim
from ultracutpro.ai.agent_s_z_p import AgentSearchZongyiProcess
from ultracutpro.utils.envs import get_env_var

import pandas as pd
import os
from loguru import logger


class ShowSearch:

    def __init__(
        self,
        target_file="data/visual_speech/ft_local/pgm_w_name_refine.csv",
        # target_visual_file="temp/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200/vis/00_info_visual.json",
        # target_visual_file="temp/vis_info/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200_info_visual.json",
        target_visual_file="temp/vis_info/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200_info_visual.json",
        target_source_video_file="",
    ) -> None:
        target_file = self.process_csv(target_file)
        self.rag = RAGSim(target_file, rewrite=False)
        target_visual_file = self.process_json(target_visual_file)
        self.rag_visual = RAGSim(
            target_visual_file,
            rewrite=False,
            chunk_method="long",
            chunk_size=130,
            overlap=30,
        )

        api_key = get_env_var("api_key")
        api_secret = get_env_var("api_secret")
        self.llm = AgentSearchZongyiProcess(api_key, api_secret, "876")

    @staticmethod
    def time_to_milliseconds(time_str):
        hours, minutes, seconds = time_str.split(":")
        seconds, milliseconds = seconds.split(",")
        total_milliseconds = (
            int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        ) * 1000 + int(milliseconds)
        return total_milliseconds

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
        if os.path.exists(output_file):
            return output_file
        else:
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                for idx, item in enumerate(data):
                    line = item["description"].replace("\n", "  ")
                    writer.writerow([f"{idx}. {line}"])
            logger.info(f"visual csv file: {output_file} saved.")
            return output_file

    def process_csv(self, input_file):
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_rag.csv"
        df = pd.read_csv(input_file)
        self.id_to_timestamp = {}
        for _, row in df.iterrows():
            start_time, end_time = row["时间戳"].split(" --> ")
            start_time_ms = self.time_to_milliseconds(start_time)
            end_time_ms = self.time_to_milliseconds(end_time)
            self.id_to_timestamp[row["index"]] = [start_time_ms, end_time_ms]
        if os.path.exists(output_file):
            return output_file
        else:
            df["formatted"] = df.apply(
                lambda row: f"{row['index']}. {row['说话人']}: {row['转录文本']}    ",
                axis=1,
            )
            df["formatted"].to_csv(
                output_file, index=False, header=False, encoding="utf-8"
            )
            return output_file

    def query(self, text, method="audio,visual"):
        all_results = {}
        if "audio" in method:
            result = self.rag.query(text, top_k=3)
            print(f"rag result: {result}")
            # print(self.id_to_timestamp)
            # llm agent get index? and then get timestamps, then cut the video
            audio_final_res = []
            for a in result:
                timestamp_summary = self.llm.get_timestamp_and_summary(a)
                # parse it.
                # get real timestamp
                ss = self.id_to_timestamp[int(timestamp_summary["start_idx"])]
                timestamp_summary["start_ms"] = [ss[0]]
                es = self.id_to_timestamp[int(timestamp_summary["end_idx"])]
                timestamp_summary["end_ms"] = [es[0]]
                audio_final_res.append(timestamp_summary)
            print(f"audio_final_res: {audio_final_res}\n\n")
            all_results["audio"] = audio_final_res
        if "visual" in method:
            result = self.rag_visual.query(text, top_k=3)
            logger.info(f"visual rag result: {result}")
            # print(self.id_to_timestamp)
            # llm agent get index? and then get timestamps, then cut the video
            visual_final_res = []
            for a in result:
                timestamp_summary = self.llm.get_visual_timestamp_and_summary(a)
                # parse it.
                # get real timestamp
                if timestamp_summary is None:
                    continue
                ss = self.id_to_timestamp_visual[int(timestamp_summary["start_idx"])]
                timestamp_summary["start_ms"] = [int(ss[0])]
                es = self.id_to_timestamp_visual[int(timestamp_summary["start_idx"])]
                timestamp_summary["end_ms"] = [int(es[1])]
                visual_final_res.append(timestamp_summary)
            print(f"visual_final_res: {visual_final_res}\n\n")
            all_results["visual"] = visual_final_res
            logger.info("visual query done..")
        logger.info(f"query done. response data: {all_results}")
        return all_results

    def show_cut_video_part(self):
        pass


# the file maybe should add event period? not just audio
ss = ShowSearch(
    "data/visual_speech/ft_local/pgm_w_name_refine.csv",
    target_visual_file="temp/vis_info/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200_info_visual.json",
    # target_visual_file="temp/vis_info/ci46e7teuhfi85cfak90_visual_1107_qwen2vl.json",
    target_source_video_file="data/visual_speech/sync/ft_local/ci46e7teuhfi85cfak90_0515-初舞台-PGM-CAM0_S001_S001_T003_transcode_114200.mp4",
)
# result = ss.query("宁静评价蔡昌霖")
# print(result)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any


app = FastAPI()


class QueryRequest(BaseModel):
    text: str
    type: str  # 'audio', 'visual', or 'both'


@app.post("/query")
async def query(request: QueryRequest) -> Any:
    try:
        if request.type not in ["audio", "visual", "both"]:
            raise ValueError(
                "Invalid query type. Must be 'audio', 'visual', or 'both'."
            )

        if request.type in ["audio", "both"]:
            results = ss.query(request.text, "audio")

        if request.type in ["visual", "both"]:
            results = ss.query(request.text, "visual")

        return {"data": results}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.info(f"got error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
