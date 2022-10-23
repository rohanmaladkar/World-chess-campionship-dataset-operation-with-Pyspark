# -*- coding: utf-8 -*-
""": Assignment_Solution_Rohan_maladkar

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GsxhiB7bTEASTroG7RokfkdCIkPikLlu
"""

!apt-get update -y

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop2.7.tgz
!tar xf spark-3.1.2-bin-hadoop2.7.tgz

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.2-bin-hadoop2.7"

!pip install -q findspark
import findspark
findspark.init()

!pip install pyspark

import pyspark
import pandas as pd
from pyspark.sql import SparkSession

import numpy as np
import gdown
from pyspark.sql.window import Window
import pyspark.sql.functions as F

spark=SparkSession.builder.appName('WCh').getOrCreate()

spark

df_pyspark_game = spark.read.option('header','true').csv('/content/drive/MyDrive/data_grokr/chess_wc_history_game_info.csv',inferSchema=True)
df_pyspark_moves = spark.read.option('header','true').csv('/content/drive/MyDrive/data_grokr/chess_wc_history_moves.csv',inferSchema=True)
df_pyspark_eco = spark.read.option('header','true').csv('/content/drive/MyDrive/data_grokr/eco_codes.csv',inferSchema=True)

df_pyspark_game.show()

df_pyspark_game.printSchema()

df_pyspark_moves.show()

df_pyspark_eco.show()

print(" df_pyspark_game","rows:",df_pyspark_game.count(),"columns:",len(df_pyspark_game.columns))
print("df_pyspark_moves","rows:",df_pyspark_moves.count(),"columns:",len(df_pyspark_moves.columns))
print("df_pyspark_eco","rows:",df_pyspark_eco.count(),"columns:",len(df_pyspark_eco.columns))

"""# ** 1. List of Winners of Each World champions Trophy**"""

df_pyspark_game.select(['winner','tournament_name']).show()
#df_pyspark.select(['winner','tournament_name']).show(2939)

var1 = df_pyspark_game.filter((df_pyspark_game.tournament_name.contains('WorldChamp')) & (~df_pyspark_game['winner'].isin(['draw'])))
var1 = var1.groupBy("tournament_name", "winner").count().orderBy("tournament_name")
win = Window.partitionBy('tournament_name').orderBy(F.col('count').desc())
var1 = var1.withColumn('row', F.row_number().over(win)).select("winner", "tournament_name","count","row").where(F.col("row")==1)
var1=var1.drop(*["count","row"])
var1.show()

#df_pyspark_moves.withColumnRenamed('player','player_name').show()

#df_pyspark = df_pyspark_moves.withColumn('number_of_wins',df_pyspark_moves['winner'])

training = spark.read.csv('/content/drive/MyDrive/data_grokr/chess_wc_history_game_info.csv',header=True,inferSchema=True)

training.show()

training.columns



# def str_lables(a):
#   if a==1:
#     return 'white'
#   elif a==0:
#     return 'black'

# from pyspark.ml.feature import VectorAssembler
# featureassembler=VectorAssembler(inputCols=["white","black"],outputCol="player_name")

#output=featureassembler.transform(training)

"""**2. List of Players with number of times they have won Tournament in descending order**"""

from pyspark.ml.feature import StringIndexer

indexer = StringIndexer(inputCols=["white","black","winner"],outputCols=["white_index","black_index","winner_index"])
df_r = indexer.fit(df_pyspark_game).transform(df_pyspark_game)
df_r.show()

from pyspark.ml.feature import VectorAssembler
coef_var = ["white_index","black_index"]
featureassembler=VectorAssembler(inputCols=coef_var,outputCol="player_name")
output = featureassembler.transform(df_r)
output.select('player_name').show()

var2 = df_pyspark_game.filter((df_pyspark_game.winner != 'draw')& (~df_pyspark_game.event.contains('KO')) & (~df_pyspark_game.event.contains('k.o')))

var2 = var2.groupBy("tournament_name", "winner").count()

win2 = Window.partitionBy('tournament_name').orderBy(F.col('count').desc())

var2 = var2.withColumn('row', F.row_number().over(win2)).where(F.col('row') == 1)

var2 = var2.drop(*["count","row","tournament_name"])

var2 = var2.groupBy("winner").count().orderBy(F.col('count').desc())

var2 = var2.withColumnRenamed("winner", "player_name")
var2 = var2.withColumnRenamed("count", "number_of_wins")

var2.show()

# final_result = output.select("player_name","winner_index")

# from pyspark.ml.regression import LinearRegression
# train_data,test_data = final_result.randomSplit([0.75,0.25])
# regressor = LinearRegression(featuresCol='player_name', labelCol='winner_index')
# model = regressor.fit(train_data)

#pd.DataFrame({"coefficients":model.coefficients}, index=coef_var)

# res = model.evaluate(test_data)
# res

# unlabled = test_data.select('player_name','winner_index')

# pred = model.transform(unlabled)

"""# **3. Most and Least Popular eco move in world championship history**"""

from pyspark.sql.functions import greatest

df_pyspark_eco.show()

var3 = df_pyspark_game.filter(df_pyspark_game.tournament_name.contains('WorldChamp'))

var3 = var3.groupBy("eco").count().orderBy(F.col('count').desc())

var3 = var3.head(1) + var3.tail(1)

var3 = spark.createDataFrame(var3)

var3 = var3.join(df_pyspark_eco, on='eco', how="inner")

var3 = var3.withColumnRenamed("count", "number_of_occurences")
var3 = var3.select("eco", "eco_name", "number_of_occurences").orderBy(F.col("number_of_occurences"))

var3.show()

"""# **4. Find the eco move with most winnings.**"""

var4 = df_pyspark_game.filter(df_pyspark_game.winner != "draw")

var4 = var4.groupby("eco").count()

var4 = var4.orderBy(F.col("count").desc())

var4 = var4.head(1)

var4 = spark.createDataFrame(var4)

var4 = var4.join(df_pyspark_eco, on="eco", how="inner").select("eco", "eco_name")

var4.show()

"""# **5. Longest and shortest game ever played in a world championship in terms of move.**"""

win5 = Window.partitionBy("game_id").orderBy(F.col('move_no_pair').desc())

var5 = df_pyspark_moves.withColumn('row', F.row_number().over(win5)).select("game_id", "move_no_pair")

var5 = var5.filter(F.col("row")==1)

var5 = var5.join(df_pyspark_game, on='game_id', how='inner').select("game_id","event","tournament_name","move_no_pair").orderBy(F.col('move_no_pair').desc())

var5 = var5.filter((df_pyspark_game.tournament_name.contains('WorldChamp')))

var5 = var5.withColumnRenamed("move_no_pair", "number_of_moves")

var5 = var5.head(1) + var5.tail(1)
var5 = spark.createDataFrame(var5)

var5.show()

"""# **6. Shortest and Longest Draw game ever Played.**"""

win6 = Window.partitionBy("game_id").orderBy(F.col('move_no_pair').desc())

var6 = df_pyspark_moves.withColumn('row', F.row_number().over(win6)).select("game_id", "move_no_pair")

var6 = var6.filter(F.col("row")==1)

var6 = var6.join(df_pyspark_game, on='game_id', how='inner').select("game_id","event","tournament_name","move_no_pair").orderBy(F.col('move_no_pair').desc())

var6 = var6.filter((df_pyspark_game.winner.contains('draw')))
var6 = var6.withColumnRenamed("move_no_pair", "number_of_moves")

var6 = var6.head(1) + var6.tail(1)
var6 = spark.createDataFrame(var6)
var6.show()

"""# **7. Most and Least rated Player.**"""

A7white = df_pyspark_game.filter(df_pyspark_game.white_elo.isNotNull())
A7white = A7white.groupBy("white").max("white_elo")
A7white = A7white.withColumnRenamed("white","player_name")

A7black = df_pyspark_game.filter(df_pyspark_game.white_elo.isNotNull())
A7black = A7black.groupBy("black").max("black_elo")
A7black = A7black.withColumnRenamed("black","player_name")

var7 = A7white.join(A7black, on='player_name', how='inner')

var7 = var7.withColumn("elo",(F.col("max(white_elo)")+F.col("max(black_elo)"))/2)

var7 = var7.drop( *["max(white_elo)", "max(black_elo)"])
var7 = var7.orderBy( F.col("elo").desc())

var7 = var7.head(1) + var7.tail(1)
var7 = spark.createDataFrame(var7)
var7.show()

"""# **8. 3rd Last Player with most Loss.**"""

var8 = df_pyspark_game.filter(~df_pyspark_game['winner'].isin(['draw']))

var8 = var8.groupBy("loser").count()

var8 = var8.withColumnRenamed("loser","player_name")
var8 = var8.orderBy(F.col("count").desc())

win8 = Window.orderBy(F.col("count").desc())

var8 = var8.withColumn("index", F.row_number().over(win8))

var8 = var8.filter((var8['index']==3))
var8 = var8.drop(*["count","index"])

var8.show()

"""# **9. How many times players with low rating won matches with their total win Count**"""

var9 = df_pyspark_game.filter(df_pyspark_game["winner_loser_elo_diff"]<0)

var9 = var9.groupBy("winner").count().orderBy(F.col('count').desc())

var9 = var9.withColumnRenamed("winner","player_name")
var9 = var9.withColumnRenamed("count","win_count")

var9.show()

"""# **10. Move Sequence for Each Player in a Match**"""

win10 = Window.partitionBy("game_id").orderBy(F.col("move_no").desc())

var10 = df_pyspark_moves.withColumn("row",F.row_number().over(win10))

var10 = var10.filter(var10.row<3)

var10 = var10.select("game_id", "player", "move_sequence", "move_no")
var10 = var10.withColumnRenamed("move_no", "move_count")
var10 = var10.withColumnRenamed("player", "player_name")

var10.show()

"""# 11. Total Number of games where losing player has more Captured score than Winning **player**"""

var11 = df_pyspark_game.where(~df_pyspark_game['winner'].isin(['draw']))
var11 = var11.join(df_pyspark_moves, on="game_id", how="inner")
win11 = Window.partitionBy("game_id").orderBy(F.col("move_no").desc())

var11 = var11.withColumn("row", F.row_number().over(win11))
var11 = var11.filter(var11.row == 1).drop("row")

var11 = var11.withColumn("loser_white",(var11['loser']==var11['white']))
var11 = var11.withColumn("loser_score",F.when(F.col("loser_white"),F.col("captured_score_for_white")).otherwise(( F.col('captured_score_for_black'))))

var11 = var11.withColumn("winner_white",(var11['winner']==var11['white']))
var11 = var11.withColumn("winner_score",F.when(F.col("winner_white"),F.col("captured_score_for_white")).otherwise(( F.col('captured_score_for_black'))))

var11 = var11.withColumn("Loser_with_higher_core",var11["loser_score"]>var11["winner_score"])
var11 = var11.filter(var11["Loser_with_higher_core"]==True)

finalwinA11 = Window.partitionBy().orderBy(F.col('game_id'))

var11 = var11.withColumn( "total_number_of_games", F.row_number().over(finalwinA11) )
var11 = var11.where( var11.total_number_of_games == var11.count() )
var11 = var11.select("total_number_of_games")

var11.show()

"""# **12. List All Perfect Tournament with Winner Name**"""

var12 = df_pyspark_game.filter((~df_pyspark_game.winner.isin(['draw'])) & (~df_pyspark_game.event.contains('KO')) & (~df_pyspark_game.event.contains('k.o')))

wvar12 = Window.partitionBy("tournament_name")

var12 = var12.withColumn( "winner_all_tournament", F.size( F.collect_set('winner').over(wvar12) ) == 1 )

var12 = var12.where( F.col("winner_all_tournament") )
var12 = var12.groupBy("tournament_name", "winner").count().orderBy("tournament_name")
var12= var12.withColumnRenamed("winner", "winner_name")
var12 = var12.select("winner_name", "tournament_name")
var12.show()

"""# **13. Player with highest winning ratio**"""

var13_data = df_pyspark_game.filter(~df_pyspark_game.winner.isin(['draw']))
var13played = var13_data.select( F.explode( F.array("white", "black" ) ).alias("player"))
var13played = var13played.groupBy("player").agg(F.count("player").alias("Games_played"))

var13won = var13_data.groupBy("winner").agg(F.count("winner").alias("Games_won"))
var13won = var13won.withColumnRenamed("winner","player")

var13ratio = var13played.join(var13won,on= "player", how="inner")
var13ratio = var13ratio.withColumn("Win_ratio",F.col("Games_won")/F.col("Games_played"))
var13ratio = var13ratio.orderBy(F.col("Win_ratio").desc())

var13 = var13ratio.head(1)
var13 = spark.createDataFrame(var13)
var13 = var13.select("player")
var13 = var13.withColumnRenamed("player", "player_name")

var13.show()

"""# **14. Player who had given checkmate with Pawn**"""

var14 = df_pyspark_moves.filter((df_pyspark_moves.is_check_mate == 1) & df_pyspark_moves.piece.contains('P'))

var14 = var14.select('player')
var14 = var14.withColumnRenamed("player", "player_name")

var14.show()

"""# **15. List games where player has won game without queen**"""

var15 = df_pyspark_moves.filter(((df_pyspark_moves['white_queen_count']==0)|(df_pyspark_moves["black_queen_count"]==0)))

var15 = var15.join(df_pyspark_game, on='game_id', how="inner")
var15 = var15.filter(df_pyspark_game.winner != 'draw')

var15 = var15.groupBy("game_id","event","winner").count().orderBy("game_id")
win15 = Window.partitionBy("game_id").orderBy(F.col("count").desc())

var15 = var15.withColumn('row', F.row_number().over(win15)).where(F.col("row")==1)
var15 = var15.select("game_id","event","winner").distinct()

var15 = var15.drop(*["count","row"])
var15 = var15.withColumnRenamed("winner","player_name")
var15.show()

"""# **Mounting** Google Drive"""

from google.colab import drive
drive.mount('/content/drive',force_remount=True)

path = os.chdir('/content/drive/MyDrive/DE_SOLUTION_Rohan_Maladkar/result')

# path = '/content/drive/MyDrive/DE_SOLUTION_Rohan_Maladkar/result'

print(os.getcwd())

"""# **Converting Spark DF to Pandas DF**"""

pandas_var1 = var1.toPandas()
pandas_var1.shape

pandas_var2 = var2.toPandas()
pandas_var2.shape

pandas_var3 = var3.toPandas()
pandas_var3.shape

pandas_var4 = var4.toPandas()
pandas_var4.shape

pandas_var5 = var5.toPandas()
pandas_var5.shape

pandas_var6 = var6.toPandas()
pandas_var6.shape

pandas_var7 = var7.toPandas()
pandas_var7.shape

pandas_var8 = var8.toPandas()
pandas_var8.shape

pandas_var9 = var9.toPandas()
pandas_var9.shape

pandas_var10 = var10.toPandas()
pandas_var10.shape

pandas_var11 = var11.toPandas()
pandas_var11.shape

pandas_var12 = var12.toPandas()
pandas_var12.shape

pandas_var13 = var13.toPandas()
pandas_var13.shape

pandas_var14 = var14.toPandas()
pandas_var14.shape

pandas_var15 = var15.toPandas()
pandas_var15.shape

pandas_var1.head()

"""# Convert the pandas dataframe to **csv**"""

df1 = pd.DataFrame(pandas_var1)
df1.to_csv("df1.csv")

df2 = pd.DataFrame(pandas_var2)
df2.to_csv("df2.csv")

df3 = pd.DataFrame(pandas_var3)
df3.to_csv("df3.csv")

df4 = pd.DataFrame(pandas_var4)
df4.to_csv("df4.csv")

df5 = pd.DataFrame(pandas_var5)
df5.to_csv("df5.csv")

df6 = pd.DataFrame(pandas_var6)
df6.to_csv("df6.csv")

df7 = pd.DataFrame(pandas_var7)
df7.to_csv("df7.csv")

df8 = pd.DataFrame(pandas_var8)
df8.to_csv("df8.csv")

df9 = pd.DataFrame(pandas_var9)
df9.to_csv("df9.csv")

df10 = pd.DataFrame(pandas_var10)
df10.to_csv("df10.csv")

df11 = pd.DataFrame(pandas_var11)
df11.to_csv("df11.csv")

df12 = pd.DataFrame(pandas_var12)
df12.to_csv("df12.csv")

df13 = pd.DataFrame(pandas_var13)
df13.to_csv("df3.csv")

df14 = pd.DataFrame(pandas_var14)
df14.to_csv("df14.csv")

df15 = pd.DataFrame(pandas_var15)
df15.to_csv("df15.csv")

