import dataclasses
from typing import List, Optional
from pandas import DataFrame


@dataclasses.dataclass
class ReportsClientQueryResult:
    main_result: List[DataFrame]
    totals_result: List[DataFrame]
    sql_query: Optional[str] = None
