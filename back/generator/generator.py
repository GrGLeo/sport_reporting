import os
import json
import pandas as pd
from openai import OpenAI
from sqlalchemy import create_engine
from back.utils.query import Query


class Generator:
    DB_URL = os.getenv("DATABASE_URL", "user_main:postgresql@localhost:5432/sporting")

    def __init__(self, sport, target, user_id):
        conn = create_engine("postgresql://" + self.DB_URL)
        self.sport = sport
        self.target = target
        self.query = Query(user_id, conn)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_last_workout(self):
        select_cols = "avg_pace, activity_id, duration, distance, avg_hr, avg_cadence, tss, recovery, endurance, tempo, threshold, vo2max, rpe"
        last_workout = self.query.get_query(table=f"{self.sport}.syn", select=select_cols, order="date", asc=False, limit=6)
        return pd.DataFrame(last_workout["data"])

    def _get_workout_lap(self, activity_id):
        select_cols = "pace, lap_id, timer, distance, hr, cadence"
        session = self.query.get_query(table=f"{self.sport}.lap", select=select_cols, wkt_id=activity_id)["data"]
        return pd.DataFrame(session)

    def _get_zones(self):
        select_cols = "recovery, endurance, tempo, threshold, vo2max"
        zones = self.query.get_query(table=f"param.run_zone", select=select_cols)["data"]
        zones = pd.DataFrame(zones)
        recovery = zones["recovery"].tolist()[0]
        endurance = zones["endurance"].tolist()[0]
        tempo = zones["tempo"].tolist()[0]
        threshold = zones["threshold"].tolist()[0]
        vo2max = zones["vo2max"].tolist()[0]
        return f"""
        recovery: {recovery} - {endurance}
        endurance: {endurance} - {tempo}
        tempo: {tempo} - {threshold}
        threshold: {threshold} - {vo2max}
        vo2max: {vo2max}+

        """

    def _generate_prompt(self):
        df = self._get_last_workout()
        clean_df = df.copy()
        clean_df.drop(columns="activity_id", inplace=True)
        prompt = f"Here are the last 6 running session for the athlete:\n{clean_df}\n"
        for i, row in df.iterrows():
            prompt += f"Here is the breakdown for the session number {i+1}.\n"
            prompt += f"{self._get_workout_lap(row['activity_id'])}\n"
        prompt += f"Here are the ahtlete running zone\n{self._get_zones()}"
        prompt += f"What would be a good training session, targetting {self.target} adaptation?"
        print(prompt)
        return prompt

    def generate_workout(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")
        with open(file_path, "r") as f:
            system_prompt = f.read()

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": self._generate_prompt()
                },
            ],
        )
        print(completion.choices[0].message.content)
        wkt = json.loads(completion.choices[0].message.content)
        return wkt


if __name__ == "__main__":
    DB_URL = os.getenv("DATABASE_llL", "user_main:postgresql@localhost:5432/sporting")
    gen = Generator("running", "884568f6-beac-436e-baaf-4049e90e8251", conn)
    wkt = gen.generate_workout()
    print(wkt)
