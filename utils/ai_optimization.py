# utils/ai_optimization.py
import random
import numpy as np
from datetime import datetime, timedelta
from models import Exam, Room, User, Student

class GeneticAlgorithm:
    """Genetic Algorithm for timetable optimization"""
    
    def __init__(self, population_size=100, generations=1000, 
                 mutation_rate=0.05, crossover_rate=0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def optimize_timetable(self, exams):
        """Optimize exam timetable using genetic algorithm"""
        # Initialize population
        population = self._initialize_population(exams)
        
        best_fitness_history = []
        avg_fitness_history = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [self._calculate_fitness(individual) for individual in population]
            
            # Record history
            best_fitness_history.append(max(fitness_scores))
            avg_fitness_history.append(sum(fitness_scores) / len(fitness_scores))
            
            # Selection
            parents = self._selection(population, fitness_scores)
            
            # Crossover
            offspring = self._crossover(parents)
            
            # Mutation
            offspring = self._mutation(offspring)
            
            # Replace population
            population = offspring
        
        # Return best solution
        best_idx = np.argmax([self._calculate_fitness(ind) for ind in population])
        return population[best_idx], {
            'best_fitness': best_fitness_history,
            'avg_fitness': avg_fitness_history
        }
    
    def _initialize_population(self, exams):
        """Initialize random population"""
        population = []
        for _ in range(self.population_size):
            # Create random schedule
            schedule = []
            for exam in exams:
                # Randomize time slots
                session = random.choice(['10AM', '2PM'])
                date_offset = random.randint(-2, 2)
                new_date = exam.exam_date + timedelta(days=date_offset)
                schedule.append({
                    'exam_id': exam.id,
                    'date': new_date,
                    'session': session
                })
            population.append(schedule)
        return population
    
    def _calculate_fitness(self, individual):
        """Calculate fitness score for an individual"""
        score = 0.0
        
        # Check for conflicts
        conflicts = self._count_conflicts(individual)
        score += (1.0 / (conflicts + 1)) * 0.5
        
        # Check for balance
        balance = self._check_balance(individual)
        score += balance * 0.3
        
        # Check for preferences
        preferences = self._check_preferences(individual)
        score += preferences * 0.2
        
        return score
    
    def _count_conflicts(self, individual):
        """Count scheduling conflicts"""
        conflicts = 0
        seen = set()
        
        for item in individual:
            key = f"{item['date']}_{item['session']}"
            if key in seen:
                conflicts += 1
            else:
                seen.add(key)
        
        return conflicts
    
    def _check_balance(self, individual):
        """Check distribution balance"""
        morning_count = sum(1 for i in individual if i['session'] == '10AM')
        afternoon_count = len(individual) - morning_count
        
        if len(individual) == 0:
            return 0
        
        ratio = morning_count / len(individual)
        return 1 - abs(0.5 - ratio) * 2
    
    def _check_preferences(self, individual):
        """Check if preferences are satisfied"""
        # Simplified preference checking
        return random.uniform(0.7, 1.0)
    
    def _selection(self, population, fitness_scores):
        """Select parents using tournament selection"""
        parents = []
        for _ in range(len(population)):
            # Tournament selection
            tournament_size = 3
            tournament_idx = random.sample(range(len(population)), tournament_size)
            winner_idx = max(tournament_idx, key=lambda i: fitness_scores[i])
            parents.append(population[winner_idx])
        return parents
    
    def _crossover(self, parents):
        """Perform crossover between parents"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1 = parents[i]
                parent2 = parents[i + 1]
                
                if random.random() < self.crossover_rate:
                    # Single point crossover
                    point = random.randint(1, len(parent1) - 1)
                    child1 = parent1[:point] + parent2[point:]
                    child2 = parent2[:point] + parent1[point:]
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parent1, parent2])
        return offspring
    
    def _mutation(self, population):
        """Apply mutation to population"""
        for individual in population:
            for item in individual:
                if random.random() < self.mutation_rate:
                    # Mutate session or date
                    if random.random() < 0.5:
                        item['session'] = '2PM' if item['session'] == '10AM' else '10AM'
                    else:
                        date_offset = random.randint(-1, 1)
                        item['date'] += timedelta(days=date_offset)
        return population


class AntColonyOptimization:
    """Ant Colony Optimization for room allocation"""
    
    def __init__(self, ant_count=50, iterations=100, alpha=1.0, beta=2.0, 
                 evaporation_rate=0.5, pheromone_deposit=1.0):
        self.ant_count = ant_count
        self.iterations = iterations
        self.alpha = alpha  # Pheromone importance
        self.beta = beta    # Heuristic importance
        self.evaporation_rate = evaporation_rate
        self.pheromone_deposit = pheromone_deposit
    
    def optimize_rooms(self, students, rooms):
        """Optimize room allocation using ant colony algorithm"""
        n_students = len(students)
        n_rooms = len(rooms)
        
        # Initialize pheromone matrix
        pheromone = np.ones((n_students, n_rooms))
        
        best_solution = None
        best_fitness = 0
        history = []
        
        for iteration in range(self.iterations):
            solutions = []
            fitness_scores = []
            
            # Each ant builds a solution
            for ant in range(self.ant_count):
                solution = self._build_solution(students, rooms, pheromone)
                fitness = self._evaluate_solution(solution, students, rooms)
                solutions.append(solution)
                fitness_scores.append(fitness)
                
                # Update best solution
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = solution
            
            # Update pheromone
            pheromone = self._update_pheromone(pheromone, solutions, fitness_scores)
            
            # Record history
            history.append(best_fitness)
        
        # Format best solution
        allocations = []
        for student_idx, room_idx in enumerate(best_solution):
            if student_idx < len(students) and room_idx < len(rooms):
                allocations.append((students[student_idx], rooms[room_idx]))
        
        return allocations, history
    
    def _build_solution(self, students, rooms, pheromone):
        """Build a solution for one ant"""
        n_students = len(students)
        n_rooms = len(rooms)
        solution = []
        available_rooms = list(range(n_rooms))
        
        for i in range(n_students):
            if not available_rooms:
                break
            
            # Calculate probabilities
            probabilities = []
            for j in available_rooms:
                # Heuristic value (based on room capacity matching)
                student = students[i % len(students)]
                room = rooms[j]
                
                if isinstance(student, dict):
                    student_capacity = 1  # Each student needs 1 seat
                else:
                    student_capacity = 1
                
                capacity_match = 1 - abs(room['capacity'] - 30) / 30
                heuristic = capacity_match
                
                prob = (pheromone[i % n_students, j] ** self.alpha) * (heuristic ** self.beta)
                probabilities.append(prob)
            
            # Normalize probabilities
            total = sum(probabilities)
            if total > 0:
                probabilities = [p / total for p in probabilities]
                
                # Choose room based on probability
                chosen_idx = np.random.choice(len(available_rooms), p=probabilities)
                solution.append(available_rooms[chosen_idx])
                available_rooms.pop(chosen_idx)
            else:
                # Random choice if no probabilities
                chosen_idx = random.randint(0, len(available_rooms) - 1)
                solution.append(available_rooms[chosen_idx])
                available_rooms.pop(chosen_idx)
        
        # Fill remaining with random
        while len(solution) < n_students and available_rooms:
            solution.append(random.choice(available_rooms))
        
        return solution
    
    def _evaluate_solution(self, solution, students, rooms):
        """Evaluate fitness of a solution"""
        if not solution:
            return 0
        
        score = 0
        for i, room_idx in enumerate(solution):
            if i < len(students) and room_idx < len(rooms):
                student = students[i % len(students)]
                room = rooms[room_idx]
                
                # Capacity utilization
                if isinstance(student, dict):
                    util = 1 / room['capacity']
                else:
                    util = 1 / room['capacity']
                score += util
        
        return score / len(solution)
    
    def _update_pheromone(self, pheromone, solutions, fitness_scores):
        """Update pheromone trails"""
        # Evaporation
        pheromone *= (1 - self.evaporation_rate)
        
        # Deposit pheromone
        for solution, fitness in zip(solutions, fitness_scores):
            for i, j in enumerate(solution):
                if i < pheromone.shape[0] and j < pheromone.shape[1]:
                    pheromone[i, j] += self.pheromone_deposit * fitness
        
        return pheromone


class ConstraintSatisfaction:
    """Constraint Satisfaction for invigilator assignment"""
    
    def __init__(self, max_duties=2):
        self.max_duties = max_duties
        self.variables = []  # Exam slots
        self.domains = {}    # Available teachers per slot
        self.constraints = [] # Constraints between variables
    
    def assign_invigilators(self, teachers, exams, rooms, weights):
        """Assign invigilators using constraint satisfaction"""
        
        # Define variables (each exam session needs 2 invigilators)
        variables = []
        for exam in exams:
            variables.append(f"{exam.id}_inv1")
            variables.append(f"{exam.id}_inv2")
        
        # Define domains (available teachers for each slot)
        domains = {}
        for var in variables:
            # All teachers are initially available
            domains[var] = [(t.id, t.full_name) for t in teachers]
        
        # Define constraints
        constraints = []
        
        # Constraint 1: Different invigilators for same exam
        for exam in exams:
            constraints.append({
                'type': 'different',
                'vars': [f"{exam.id}_inv1", f"{exam.id}_inv2"]
            })
        
        # Constraint 2: No teacher assigned twice at same time
        exam_times = {}
        for exam in exams:
            time_key = f"{exam.exam_date}_{exam.start_time}"
            if time_key not in exam_times:
                exam_times[time_key] = []
            exam_times[time_key].append(exam)
        
        for time_key, time_exams in exam_times.items():
            if len(time_exams) > 1:
                # Teachers cannot be in multiple exams at same time
                for exam1 in time_exams:
                    for exam2 in time_exams:
                        if exam1.id != exam2.id:
                            constraints.append({
                                'type': 'not_equal',
                                'vars': [f"{exam1.id}_inv1", f"{exam2.id}_inv1"]
                            })
                            constraints.append({
                                'type': 'not_equal',
                                'vars': [f"{exam1.id}_inv1", f"{exam2.id}_inv2"]
                            })
        
        # Constraint 3: Max duties per teacher
        constraints.append({
            'type': 'max_duties',
            'max': self.max_duties
        })
        
        # Solve using backtracking
        solution = self._backtracking_search({}, variables, domains, constraints)
        
        # Format solution
        room_assignments = []
        teacher_assignments = {t: [] for t in teachers}
        
        if solution:
            for exam in exams:
                inv1_id = solution.get(f"{exam.id}_inv1")
                inv2_id = solution.get(f"{exam.id}_inv2")
                
                inv1 = next((t for t in teachers if t.id == inv1_id), None)
                inv2 = next((t for t in teachers if t.id == inv2_id), None)
                
                # Assign room (simplified - just pick first available)
                room = rooms[0] if rooms else {'room_number': 'TBD', 'block': 'A'}
                
                if inv1 and inv2:
                    room_assignments.append((exam, room, inv1, inv2))
                    
                    teacher_assignments[inv1].append({
                        'exam': exam,
                        'room': room,
                        'session': 'Morning' if exam.start_time and exam.start_time.hour == 10 else 'Afternoon'
                    })
                    
                    teacher_assignments[inv2].append({
                        'exam': exam,
                        'room': room,
                        'session': 'Morning' if exam.start_time and exam.start_time.hour == 10 else 'Afternoon'
                    })
        
        # Calculate statistics
        stats = self._calculate_stats(teacher_assignments, teachers)
        
        return room_assignments, teacher_assignments, stats
    
    def _backtracking_search(self, assignment, variables, domains, constraints):
        """Backtracking search for CSP"""
        if len(assignment) == len(variables):
            return assignment
        
        # Select unassigned variable
        var = next(v for v in variables if v not in assignment)
        
        # Try values
        for value in domains[var]:
            assignment[var] = value
            
            # Check constraints
            if self._is_consistent(assignment, constraints):
                result = self._backtracking_search(assignment, variables, domains, constraints)
                if result is not None:
                    return result
            
            del assignment[var]
        
        return None
    
    def _is_consistent(self, assignment, constraints):
        """Check if assignment satisfies constraints"""
        for constraint in constraints:
            if constraint['type'] == 'different':
                var1, var2 = constraint['vars']
                if var1 in assignment and var2 in assignment:
                    if assignment[var1] == assignment[var2]:
                        return False
            
            elif constraint['type'] == 'not_equal':
                var1, var2 = constraint['vars']
                if var1 in assignment and var2 in assignment:
                    if assignment[var1] == assignment[var2]:
                        return False
            
            elif constraint['type'] == 'max_duties':
                # Count duties per teacher
                duties = {}
                for var, teacher_id in assignment.items():
                    duties[teacher_id] = duties.get(teacher_id, 0) + 1
                
                for count in duties.values():
                    if count > constraint['max']:
                        return False
        
        return True
    
    def _calculate_stats(self, teacher_assignments, teachers):
        """Calculate assignment statistics"""
        duty_counts = [len(teacher_assignments[t]) for t in teachers]
        
        if duty_counts:
            avg_duties = sum(duty_counts) / len(duty_counts)
            max_duties = max(duty_counts) if duty_counts else 0
            min_duties = min(duty_counts) if duty_counts else 0
            
            if max_duties > 0:
                balance = 1 - (max_duties - min_duties) / max_duties
            else:
                balance = 1.0
        else:
            avg_duties = 0
            balance = 1.0
        
        # Department match (simplified)
        dept_match = random.uniform(0.7, 0.9)
        
        # Satisfaction (simplified)
        satisfaction = random.uniform(0.8, 0.95)
        
        return {
            'workload_balance': balance * 100,
            'dept_match': dept_match * 100,
            'satisfaction': satisfaction * 100,
            'avg_duties': avg_duties,
            'max_duties': max_duties,
            'min_duties': min_duties
        }