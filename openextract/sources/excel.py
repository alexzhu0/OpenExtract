"""Excel data source for OpenExtract."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import pandas as pd

from openextract.pipelines.base import Document


class ExcelSource:
    """Read documents from Excel file."""
    
    def __init__(
        self,
        path: str | Path,
        sheet: str | int = 0,
        id_column: str = "Id",
        title_column: str = "Title",
        content_column: str = "Content",
        max_rows: Optional[int] = None,
    ):
        """
        Initialize Excel source.
        
        Args:
            path: Path to Excel file
            sheet: Sheet name or index
            id_column: Column name for document ID
            title_column: Column name for document title
            content_column: Column name for document content
            max_rows: Optional limit on number of rows to process
        """
        self.path = Path(path)
        self.sheet = sheet
        self.id_column = id_column
        self.title_column = title_column
        self.content_column = content_column
        self.max_rows = max_rows
        
        if not self.path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.path}")
    
    def __iter__(self) -> Iterator[Document]:
        """Yield Document objects from Excel rows."""
        df = pd.read_excel(
            self.path,
            sheet_name=self.sheet,
            nrows=self.max_rows,
        )
        
        for idx, row in df.iterrows():
            doc_id = str(row.get(self.id_column, f"row_{idx}"))
            title = str(row.get(self.title_column, ""))
            payload = str(row.get(self.content_column, ""))
            
            # Collect remaining columns as metadata
            meta: Dict[str, Any] = {}
            for col in df.columns:
                if col not in [self.id_column, self.title_column, self.content_column]:
                    meta[col] = row[col]
            
            yield Document(
                doc_id=doc_id,
                title=title,
                payload=payload,
                meta=meta,
            )
