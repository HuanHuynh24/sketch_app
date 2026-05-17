from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.university import UniversityProgram
from app.schemas.program import ProgramSearchRequest


class ProgramService:
    def __init__(self, db: Session):
        self.db = db

    def search_programs(self, payload: ProgramSearchRequest) -> list[UniversityProgram]:
        """
        Tìm kiếm các chương trình học dựa trên dữ liệu có cấu trúc.
        """
        query = self.db.query(UniversityProgram)

        # Filter theo danh sách quốc gia (nếu có)
        if payload.countries:
            country_filters = [
                UniversityProgram.country.ilike(f"%{c}%") 
                for c in payload.countries
            ]
            query = query.filter(or_(*country_filters))

        # Filter theo ngành học (nếu có)
        if payload.majors:
            major_filters = [
                UniversityProgram.major_name.ilike(f"%{m}%") 
                for m in payload.majors
            ]
            query = query.filter(or_(*major_filters))

        # Lọc học phí tối đa (Ngân sách)
        if payload.max_tuition is not None:
            # Giả định tuition_fee là USD
            query = query.filter(
                (UniversityProgram.tuition_fee == None) | 
                (UniversityProgram.tuition_fee <= payload.max_tuition)
            )

        # Lọc IELTS tối thiểu
        if payload.min_ielts is not None:
            # Những trường không yêu cầu IELTS (None) hoặc yêu cầu <= IELTS của học sinh
            query = query.filter(
                (UniversityProgram.ielts_requirement == None) | 
                (UniversityProgram.ielts_requirement <= payload.min_ielts)
            )

        # Giới hạn trả về top 20 kết quả phù hợp nhất trong PostgreSQL
        return query.limit(20).all()

    def bulk_create_programs(self, programs: list[ProgramSearchRequest]) -> list[UniversityProgram]:
        from app.models.university import UniversityProgram, University
        
        created = []
        for p in programs:
            db_program = UniversityProgram(
                university_name=p.university_name,
                country=p.country,
                city=p.city,
                major_name=p.major_name,
                degree_level=p.degree_level,
                tuition_fee=p.tuition_fee,
                currency=p.currency,
                ielts_requirement=p.ielts_requirement,
                source_url=getattr(p, 'source_url', None)
            )
            self.db.add(db_program)
            created.append(db_program)
        
        self.db.commit()
        for p in created:
            self.db.refresh(p)
        return created
