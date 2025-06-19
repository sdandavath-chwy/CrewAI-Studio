from crewai.tools import BaseTool
import pandas as pd
from typing import Literal
from io import StringIO
import json

class AnalyticsTool(BaseTool):
    name: Literal["Analytics Tool"] = "Analytics Tool"
    description: Literal["Performs basic analytics on revenue data"] = "Performs basic analytics on revenue data"

    def _run(self, content: str) -> str:
        try:
            # Attempt to parse content as JSON for a 'content' field
            try:
                parsed = json.loads(content)
                csv_content = parsed.get("content", content)
            except json.JSONDecodeError:
                csv_content = content

            df = pd.read_csv(StringIO(csv_content))
            result = {
                "min_revenue": df["NET_REVENUE"].min(),
                "max_revenue": df["NET_REVENUE"].max(),
                "first_above_10m": df[df["NET_REVENUE"] > 10].iloc[0]["ORDER_WEEK"]
                    if not df[df["NET_REVENUE"] > 10].empty else None
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in analytics: {e}"
