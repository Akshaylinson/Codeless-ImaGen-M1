from __future__ import annotations

import time
from dataclasses import asdict

from ..database.sqlite import db_session


class JobService:
    def create_job(self, user_id: int | None, image_id: int, instruction: str) -> int:
        with db_session() as connection:
            cursor = connection.execute(
                """
                INSERT INTO jobs (user_id, image_id, instruction, status, progress)
                VALUES (?, ?, ?, 'queued', 0)
                """,
                (user_id, image_id, instruction),
            )
            job_id = int(cursor.lastrowid)
            connection.execute(
                "INSERT INTO activity_logs (user_id, action, detail) VALUES (?, ?, ?)",
                (user_id, "job_created", f"job_id={job_id}"),
            )
            return job_id

    def update_job(
        self,
        job_id: int,
        *,
        status: str | None = None,
        progress: int | None = None,
        error_message: str | None = None,
        output_path: str | None = None,
        processing_time: float | None = None,
    ) -> None:
        assignments = []
        values: list[object] = []
        if status is not None:
            assignments.append("status = ?")
            values.append(status)
        if progress is not None:
            assignments.append("progress = ?")
            values.append(progress)
        if error_message is not None:
            assignments.append("error_message = ?")
            values.append(error_message)
        if output_path is not None:
            assignments.append("output_path = ?")
            values.append(output_path)
        if processing_time is not None:
            assignments.append("processing_time = ?")
            values.append(processing_time)
        assignments.append("updated_at = CURRENT_TIMESTAMP")
        sql = f"UPDATE jobs SET {', '.join(assignments)} WHERE id = ?"
        values.append(job_id)
        with db_session() as connection:
            connection.execute(sql, values)

    def set_failed(self, job_id: int, error_message: str) -> None:
        self.update_job(job_id, status="failed", progress=100, error_message=error_message)

    def set_completed(self, job_id: int, output_path: str, processing_time: float) -> None:
        self.update_job(job_id, status="completed", progress=100, output_path=output_path, processing_time=processing_time)

    def get_job(self, job_id: int) -> dict | None:
        with db_session() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(row) if row else None

    def list_jobs(self, limit: int = 100) -> list[dict]:
        with db_session() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    def delete_job(self, job_id: int) -> None:
        with db_session() as connection:
            connection.execute("DELETE FROM generated_images WHERE job_id = ?", (job_id,))
            connection.execute("DELETE FROM edit_requests WHERE job_id = ?", (job_id,))
            connection.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

