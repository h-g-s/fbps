library("irace")
parameters <- readParameters("parameters-cbc-lr-dual.txt")
scenario <- readScenario(filename = "scenarioCbc-lr-dual.txt", scenario = defaultScenario())
irace(scenario = scenario, parameters = parameters)