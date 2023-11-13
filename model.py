from mip import Model, xsum, minimize, maximize, CONTINUOUS, INTEGER, BINARY, OptimizationStatus, CPLEX

class Shifts:
    def __init__(self) -> None:
        self.model = Model()

    def sets(self, sets):
        self.Forecast = sets['Forecast']
        self.Shifts = sets['Shifts']

    def parameters(self, parameters):
        self.Cost = parameters['Cost']
        self.A = parameters['A']

    def variables(self):
        self.x = [self.model.add_var(var_type=INTEGER,name=f"number person in shift {self.Shifts[j]}") for j in self.Shifts]

    def constrains(self):
        for i in self.Forecast:
            self.model += xsum(self.A[i][j] * self.x[j] for j in self.Shifts) >= self.Forecast[i]

    def objetive(self):
        self.model.objective = minimize(xsum(self.Cost[j] * self.x[j] for j in self.Shifts))
    
    def execute(self):
        self.model.optimize()
        print(f"Status: {self.model.status}")
        Workforce = 0
        shifts_result = {}
        for j in self.Shifts:
            # print(f"{self.x[j].name} : {int(self.x[j].x)}")
            shifts_result[j] = int(self.x[j].x)
            Workforce +=int(self.x[j].x)

        return {'W':Workforce, "Shifts":shifts_result}
    