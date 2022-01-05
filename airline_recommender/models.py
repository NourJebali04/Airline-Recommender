from .utils import DBConnect

conn = DBConnect("neo4j://localhost:7687", "neo4j", "1234")

def find_airlines(airportsrc, airportdest):
    return conn.find_airline_to_go_to_from(airportsrc, airportdest)

def best_airlines():
    return conn.find_best_airline()

def find_destinations_of(airline):
    return conn.find_destinations(airline)

print(find_airlines("Domodedovo International Airport", "Begishevo Airport"))
print('------------')
print(best_airlines())
print('------------')
for l in best_airlines():
    print(l,': ', find_destinations_of(l))