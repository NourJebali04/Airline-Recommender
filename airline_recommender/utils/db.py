from neo4j import GraphDatabase
from py2neo import Graph, Path

import logging
from neo4j.exceptions import ServiceUnavailable



''' uri = "neo4j://localhost:7687"
user = "neo4j"
password = "1234" '''

class DBConnect:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self.driver.close()


    def find_destinations(self, airline_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_dest, airline_name)
            return  result

    @staticmethod
    def _find_and_return_dest(tx, airline_name):

        query1 = (
            "MATCH (p:Airline{name: $airline_name})-[r:hasFlight]->(n:Route) "
            "RETURN DISTINCT n.destAirport AS IATA"
        )
        result1 = tx.run(query1, airline_name=airline_name)
        IATA = [record["IATA"] for record in result1]

        query2 =(
            "MATCH (n:Airport) "
            "WHERE n.IATA IN $IATA "
            "RETURN n.name AS airport"
        )
        result2 = tx.run(query2, IATA=IATA)
        airportDestinations= [record["airport"] for record in result2]

        return airportDestinations



    def find_best_airline(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_best)
            return  result

    @staticmethod
    def _find_and_return_best(tx):
        query = (
            #"MATCH (p: Airport {name: $airport_name})-[r:to]->(airport)"
            #"MATCH (n: Airport) "
            #"WHERE n.name = $airport_name "
            #"RETURN n.TimeZone"
            "MATCH (p:AirlineSentiment{airlineSentiment:'positive'})-[r:hasImpressionOn]->(n:Airline)"
            "RETURN n.name AS AirlineName, AVG(toFloat(p.airlineSentimentConfidence)) AS avrg ORDER BY avrg"

        )
        result = tx.run(query)

        bestAirlines= [record["AirlineName"] for record in result]
        return bestAirlines


    def find_best_airlines_destination(self):
        bestAirlines = self.find_best_airline()
        for airline in bestAirlines:
            if airline == 'United':
                united = self.find_destinations('United Airlines')
            elif airline == 'Delta':
                delta = self.find_destinations('Delta Air Lines')
            elif airline == 'American':
                american = self.find_destinations('American Airlines')
            elif airline == 'Southwest':
                southwest = self.find_destinations('Southwest Airlines')
            elif airline == 'Virgin America':
                virgin = self.find_destinations("Virgin America")
            elif airline == 'US Airways':
                us = self.find_destinations("US Airways")
        destionations = {'Unites Airlines':united, 'Delta Airlines':delta,
                         'American Airlines': american, 'Southwest Airlines': southwest,
                         'Virgin America':virgin, 'US Airways':us }
        return destionations



    def find_airline_to_go_to_from(self, airportsrc, airportdest):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_airline_to_go_to, airportsrc, airportdest)
            return result

    @staticmethod
    def _find_and_return_airline_to_go_to(tx, airportsrc, airportdest):
        query1 =(
            "MATCH (n:Airport) "
            "WHERE n.name=$airportsrc "
            "RETURN n.IATA AS IATAsrc"
        )
        result1 = tx.run(query1, airportsrc=airportsrc)
        IATAsrc = [record["IATAsrc"] for record in result1][0]

        query2 = (
            "MATCH (n:Airport) "
            "WHERE n.name=$airportdest "
            "RETURN n.IATA AS IATAdest"
        )
        result2 = tx.run(query2, airportdest=airportdest)
        IATAdest = [record["IATAdest"] for record in result2][0]

        query = (
            "MATCH (p: Airline)-[r:hasFlight]->(n:Route) "
            "WHERE n.sourceAirport=$IATAsrc AND n.destAirport=$IATAdest "
            "RETURN DISTINCT p.name AS AirlineName"

        )
        result = tx.run(query, IATAsrc=IATAsrc, IATAdest=IATAdest)

        airlines= [record["AirlineName"] for record in result]
        return airlines

    def recommender(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_users_items)
            authors=result[0]
            airlines=result[1]
            rateMat = [[0] * len(authors) for i in range(len(airlines))]
            for i in range (1,100):
                for j in range (1,len(airlines)):
                    if ((airlines[j]!='') & (authors[i]!='') & (self.getRate(airlines[j], authors[i])!='')):
                        rateMat[i][j] = self.getRate(airlines[j], authors[i])

            return  rateMat[0][0], rateMat[40][56], rateMat[1000][560],

    @staticmethod
    def _find_users_items(tx):
        query1 = (
            "MATCH (p:Traveller)-[r:ratedAirline]->(n:Airline)"
            "RETURN DISTINCT p.name AS Author"
        )
        result1 = tx.run(query1)
        authors= [record["Author"] for record in result1]

        query2 = (
            "MATCH (p:Traveller)-[r:ratedAirline]->(n:Airline)"
            "RETURN DISTINCT n.name AS Airline"
        )
        result2 = tx.run(query2)
        airlines = [record["Airline"] for record in result2]

        return authors, airlines



    def getRate(self, airline, author):
        with self.driver.session() as session:
            rate = session.read_transaction(self._find_rate, airline, author)
            return rate

    @staticmethod
    def _find_rate(tx, airline, author):
        query1 = (
            "MATCH (p:Traveller)-[r:ratedAirline]->(n:Airline) "   
            "WHERE n.name=$airline AND p.name=$author "
            "RETURN p.rate AS rate"
        )
        result1 = tx.run(query1, airline=airline, author=author)
        rate= [record["rate"] for record in result1]

        return rate



# just trying to test the connection
conn = DBConnect("neo4j://localhost:7687", "neo4j", "1234")
#dest = conn.find_destinations("Virgin America")
#best = conn.find_best_airline()
#bestdest = conn.find_best_airlines_destination()
#print(conn.find_airline_to_go_to_from('Domodedovo International Airport','Begishevo Airport'))
print(conn.recommender())
#print(conn.getRate('Turkish Airlines', 'John Choi'))


conn.close()