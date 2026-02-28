# utils/attendance_ml.py
class AttendanceMLPredictor:
    @staticmethod
    def analyze_class_trend(attendance_list):
        if not attendance_list:
            return {
                'total_students': 0,
                'safe_count': 0,
                'moderate_count': 0,
                'high_risk_count': 0,
                'critical_count': 0,
                'average': 0,
                'risk_percent': 0
            }
        total = len(attendance_list)
        safe = sum(1 for a in attendance_list if a >= 75)
        moderate = sum(1 for a in attendance_list if 70 <= a < 75)
        high_risk = sum(1 for a in attendance_list if 60 <= a < 70)
        critical = sum(1 for a in attendance_list if a < 60)
        avg_attendance = sum(attendance_list) / total
        risk_percent = ((moderate + high_risk + critical) / total) * 100
        return {
            'total_students': total,
            'safe_count': safe,
            'moderate_count': moderate,
            'high_risk_count': high_risk,
            'critical_count': critical,
            'average': round(avg_attendance, 1),
            'risk_percent': round(risk_percent, 1)
        }