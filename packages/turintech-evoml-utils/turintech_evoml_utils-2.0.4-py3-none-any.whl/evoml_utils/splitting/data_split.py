from pydantic import BaseModel


from typing import List, Optional


class FitEvalSplit(BaseModel):
    """
    Stores the indices which divide a dataset into fitting and evaluation sets.
    Can be optionally labelled with an index.
    """

    index: Optional[int] = None
    fit_indices: List[int]
    eval_indices: List[int]
