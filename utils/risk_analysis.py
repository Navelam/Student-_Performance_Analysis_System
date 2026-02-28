# utils/risk_analysis.py
import random

class RiskAnalyzer:
    @staticmethod
    def calculate_grade(final_marks):
        if final_marks >= 18:
            return 'A+'
        elif final_marks >= 15:
            return 'A'
        elif final_marks >= 12:
            return 'B'
        elif final_marks >= 10:
            return 'C'
        else:
            return 'D'
    
    @staticmethod
    def calculate_risk_status(final_marks, attendance_percentage):
        if attendance_percentage < 70:
            return 'Critical'
        elif final_marks < 10:
            return 'Critical'
        elif final_marks < 15:
            return 'Average'
        elif final_marks >= 18:
            return 'Best'
        else:
            return 'Safe'
    
    @staticmethod
    def predict_risk_probability(student_data):
        features = [
            student_data.get('attendance_percentage', 0) / 100,
            student_data.get('internal1', 0) / 70,
            student_data.get('internal2', 0) / 70,
            student_data.get('assessment', 0) / 10,
            student_data.get('seminar', 0) / 10
        ]
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        score = sum(f * w for f, w in zip(features, weights))
        risk_probability = 1 - min(1, max(0, score))
        risk_probability += random.uniform(-0.05, 0.05)
        return round(max(0, min(1, risk_probability)), 2)
    
    @staticmethod
    def analyze_batch(performances):
        stats = {
            'total': len(performances),
            'critical': 0,
            'average': 0,
            'safe': 0,
            'best': 0,
            'avg_marks': 0,
            'avg_attendance': 0
        }
        total_marks = 0
        total_attendance = 0
        for perf in performances:
            total_marks += perf.final_marks
            total_attendance += perf.attendance_percentage
            if perf.risk_status == 'Critical':
                stats['critical'] += 1
            elif perf.risk_status == 'Average':
                stats['average'] += 1
            elif perf.risk_status == 'Best':
                stats['best'] += 1
            else:
                stats['safe'] += 1
        if performances:
            stats['avg_marks'] = round(total_marks / len(performances), 1)
            stats['avg_attendance'] = round(total_attendance / len(performances))
        return stats
    
    @staticmethod
    def get_improvement_suggestion(final_marks):
        if final_marks >= 18:
            return "Excellent performance! Keep it up!"
        elif final_marks >= 15:
            needed = 18 - final_marks
            return f"Need {needed} more marks to reach A+ grade."
        elif final_marks >= 12:
            needed_a = 15 - final_marks
            needed_aplus = 18 - final_marks
            return f"Need {needed_a} marks for A grade, {needed_aplus} for A+."
        elif final_marks >= 10:
            needed = 12 - final_marks
            return f"Need {needed} marks to reach B grade."
        else:
            needed_pass = 10 - final_marks
            return f"CRITICAL: Need {needed_pass} marks to pass. Immediate attention required!"