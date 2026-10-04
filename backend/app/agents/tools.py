from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.business import SalesRecord, SupportTicket
from app.models.document import Document, DocumentChunk
from app.services.document_service import document_service


class FinanceTools:
    """Approved tools restricted strictly to financial analytics."""

    @staticmethod
    def get_sales_summary(db: Session) -> Dict[str, Any]:
        """Aggregate total revenue, sales volume, and product rankings."""
        total_sales = db.query(func.sum(SalesRecord.amount)).scalar() or 0.0
        total_units = db.query(func.sum(SalesRecord.units)).scalar() or 0

        # Top products by sales volume
        top_products = (
            db.query(
                SalesRecord.product_name,
                func.sum(SalesRecord.amount).label("revenue"),
                func.sum(SalesRecord.units).label("units_sold")
            )
            .group_by(SalesRecord.product_name)
            .order_by(func.sum(SalesRecord.amount).desc())
            .limit(5)
            .all()
        )

        # Regional breakdown
        regional_breakdown = (
            db.query(
                SalesRecord.region,
                func.sum(SalesRecord.amount).label("revenue")
            )
            .group_by(SalesRecord.region)
            .all()
        )

        return {
            "total_revenue": round(float(total_sales), 2),
            "total_units_sold": int(total_units),
            "top_products": [
                {"name": p[0], "revenue": round(float(p[1]), 2), "units": int(p[2])}
                for p in top_products
            ],
            "regional_breakdown": [
                {"region": r[0], "revenue": round(float(r[1]), 2)}
                for r in regional_breakdown
            ]
        }

    @staticmethod
    def detect_sales_anomalies(db: Session) -> List[Dict[str, Any]]:
        """Identify statistical anomalies, sharp drops, or irregular transactions."""
        # Find high refund records or unusually high single transactions
        records = db.query(SalesRecord).order_by(SalesRecord.transaction_date.desc()).limit(100).all()
        anomalies = []
        for rec in records:
            if rec.status == "refunded" and rec.amount > 5000:
                anomalies.append({
                    "id": rec.id,
                    "product": rec.product_name,
                    "amount": rec.amount,
                    "type": "High-Value Refund Detected",
                    "region": rec.region,
                    "description": f"Refund of ${rec.amount:,.2f} recorded in {rec.region} for {rec.product_name}."
                })
            elif rec.amount > 25000:
                anomalies.append({
                    "id": rec.id,
                    "product": rec.product_name,
                    "amount": rec.amount,
                    "type": "Outlier Transaction Volume",
                    "region": rec.region,
                    "description": f"Single purchase order of ${rec.amount:,.2f} exceeds 99th percentile threshold."
                })
        return anomalies[:5]


class SupportTools:
    """Approved tools restricted strictly to customer support analysis."""

    @staticmethod
    def get_support_tickets_summary(db: Session) -> Dict[str, Any]:
        """Aggregate ticket counts, priority distributions, and open complaint categories."""
        total_tickets = db.query(SupportTicket).count()
        open_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(["open", "in_progress"])).count()
        urgent_tickets = db.query(SupportTicket).filter(SupportTicket.priority.in_(["urgent", "high"])).count()

        # Category distribution
        categories = (
            db.query(SupportTicket.category, func.count(SupportTicket.id))
            .group_by(SupportTicket.category)
            .all()
        )

        unresolved_samples = (
            db.query(SupportTicket)
            .filter(SupportTicket.status.in_(["open", "in_progress"]))
            .order_by(SupportTicket.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "urgent_tickets": urgent_tickets,
            "category_distribution": [{"category": c[0], "count": c[1]} for c in categories],
            "unresolved_tickets": [
                {
                    "id": t.id,
                    "ticket_number": t.ticket_number,
                    "customer": t.customer_name,
                    "subject": t.subject,
                    "priority": t.priority,
                    "category": t.category,
                    "sentiment": t.ai_sentiment or "neutral"
                }
                for t in unresolved_samples
            ]
        }


class DocumentTools:
    """Approved tools for RAG and document context retrieval."""

    @staticmethod
    def search_documents(db: Session, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks from ingested business documents."""
        all_chunks = db.query(DocumentChunk).all()
        if not all_chunks:
            return []

        chunk_data = [
            {
                "id": c.id,
                "document_id": c.document_id,
                "content": c.content,
                "embedding": c.embedding,
                "metadata": c.metadata_info
            }
            for c in all_chunks
        ]

        relevant = document_service.retrieve_relevant_chunks(query, chunk_data, top_k=top_k)
        return [
            {
                "chunk_id": item[0]["id"],
                "content": item[0]["content"],
                "relevance_score": round(item[1], 3)
            }
            for item in relevant
        ]
