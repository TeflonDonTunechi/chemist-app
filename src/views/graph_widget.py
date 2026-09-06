from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from src.database import Session
from src.models import Sale
from sqlalchemy import func

class SalesGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.figure = Figure(figsize=(8, 3), dpi=100, facecolor='#f5f6fa')
        self.canvas = FigureCanvas(self.figure)
        self.layout().addWidget(self.canvas)
        self.current_period = "Daily"
        self.load_data("Daily")

    def load_data(self, period="Daily"):
        self.current_period = period
        sess = Session()
        
        # Group by different time periods
        if period == "Hourly":
            # Last 24 hours grouped by hour - SQLite compatible
            cutoff = datetime.now() - timedelta(days=1)
            sales = sess.query(
                func.strftime('%Y-%m-%d %H:00:00', Sale.timestamp).label('time'),
                func.sum(Sale.total_amount).label('total')
            ).filter(
                Sale.timestamp >= cutoff
            ).group_by('time').order_by('time').all()
            x_label = "Hour"
            date_format = '%Y-%m-%d %H:00'
        elif period == "Weekly":
            sales = sess.query(
                func.strftime('%Y-%W', Sale.timestamp).label('week'),
                func.sum(Sale.total_amount).label('total')
            ).group_by('week').order_by('week').all()
            x_label = "Week"
            date_format = '%Y-%W'
        elif period == "Monthly":
            sales = sess.query(
                func.strftime('%Y-%m', Sale.timestamp).label('month'),
                func.sum(Sale.total_amount).label('total')
            ).group_by('month').order_by('month').all()
            x_label = "Month"
            date_format = '%Y-%m'
        else:  # Daily (default)
            sales = sess.query(
                func.date(Sale.timestamp).label('date'),
                func.sum(Sale.total_amount).label('total')
            ).group_by(func.date(Sale.timestamp)).order_by('date').all()
            x_label = "Date"
            date_format = '%Y-%m-%d'
        
        sess.close()
        
        if not sales:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No sales data yet", ha='center', va='center', fontsize=12)
            ax.set_axis_off()
            self.canvas.draw()
            return

        # Parse dates
        dates = []
        totals = []
        for row in sales:
            try:
                if period == "Hourly":
                    dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                elif period == "Weekly":
                    # Parse week number
                    year, week = row[0].split('-')
                    # Get first day of that week
                    dt = datetime.strptime(f"{year}-W{week}-1", '%Y-W%W-%w')
                elif period == "Monthly":
                    dt = datetime.strptime(row[0], '%Y-%m')
                else:
                    dt = datetime.strptime(row[0], '%Y-%m-%d')
                dates.append(dt)
                totals.append(row[1])
            except:
                continue

        if not dates:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No sales data yet", ha='center', va='center', fontsize=12)
            ax.set_axis_off()
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        ax.plot(dates, totals, marker='o', linestyle='-', color='#6c3b9e', linewidth=2, markersize=4)
        ax.fill_between(dates, totals, color='#6c3b9e', alpha=0.1)
        ax.set_xlabel(x_label)
        ax.set_ylabel("KES")
        
        # Format x-axis based on period
        if period == "Hourly":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        elif period == "Weekly":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('W%W'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        elif period == "Monthly":
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        
        self.figure.autofmt_xdate()
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f5f6fa')
        self.figure.tight_layout()
        self.canvas.draw()