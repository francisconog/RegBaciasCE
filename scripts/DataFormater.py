import os
import argparse
from glob import glob
import numpy as np
import pandas as pd


parser = argparse.ArgumentParser(description='Data Formater for file: dados.xls ')


parser.add_argument("--filePath", "-x", default=None, help="Created file name and path",type=str)
parser.add_argument("--fileName", "-f", help="Created file name and path",type=str)
parser.add_argument("--normalize", "-n", default=None, help="Created file must be normalized",  action='store_true')
parser.add_argument("--evapotranspiration", "-e", default=None, help="Number of observations of evapotranspiration", type=int)
parser.add_argument("--precipitation", "-p", default=None, help="Number of observations of precipitation", type=int)
parser.add_argument("--flow", "-q", default=None, help="Number of observations of flow rate", type=int)
# python DataFormater.py -x /Users/franciscomatos/OneDrive/Code/DEHA/RegBaciasCE/database/input \
#                         -f DadosFFN_IC.csv \
#                         -n \
#                         -e 0 \
#                         -p 6 \
#                         -q 1

args = parser.parse_args()

path = args.filePath
if path == None:
    path = ""
else:
    path = path
fileName = args.fileName
eLength = args.evapotranspiration
pLength = args.precipitation
qLength = args.flow

def ShiftAndConcat(df,col,n):
    for i in range(n):
        if i ==0:
            temp = df[col]
        else:
            temp = pd.concat([temp,df[col].shift(-i)],axis=1)
            
    temp.columns = [col+"_%d" % (n-1-j) for j in range(n)]
    return temp


def FormatData(db,basins, caracUtilizadas,Plag,Elag,Qlag):
    i = max([Plag,Elag,Qlag])

    for k in range(len(basins)):
        PEQbasin = db.parse(basins[k])
        PEQbasin = PEQbasin.set_index("Data")
        Q = ShiftAndConcat(PEQbasin,"Q",i)
        P = ShiftAndConcat(PEQbasin,"P",i)
        E = ShiftAndConcat(PEQbasin,"E",i)
        dfBasin = pd.concat([E,P,Q],axis=1)
        colNames = dfBasin.columns
        for col in colNames:
            dfBasin = dfBasin.query("%s != -999" % col)
        dfBasin
        caracBasin = caracUtilizadas[caracUtilizadas["Estações ANA"] == int(basins[k])]
        caracBasinMatrix = np.ones((dfBasin.shape[0],caracBasin.shape[1])) * caracBasin.values
        caracBasinDf = pd.DataFrame(caracBasinMatrix,columns=caracBasin.columns)
        dfFormatted = pd.concat([caracBasinDf,dfBasin.reset_index().drop("Data",axis=1)],axis=1)
        if k == 0:
            dfCompleted = dfFormatted
        else:
            dfCompleted = pd.concat([dfCompleted, dfFormatted], axis=0)
    dfCompleted = dfCompleted.loc[dfCompleted.Q_0.notnull()]
    if Qlag < i:
        dfCompleted = dfCompleted.drop(["Q_%d" % (j) for j in range(Qlag,i)],axis=1)
    if Plag < i:
        dfCompleted = dfCompleted.drop(["P_%d" % (j) for j in range(Plag,i)],axis=1)
    if Elag < i:
        dfCompleted = dfCompleted.drop(["E_%d" % (j) for j in range(Elag,i)],axis=1)
        
    dfCompleted["Estações ANA"] = dfCompleted["Estações ANA"].astype(int).astype(str)
    return dfCompleted

def main():
    caracFisicas = pd.read_excel("../database/input/dados.xls",sheet_name="Resultados")
    caracFisicas = caracFisicas.drop(["SAT","PES","Nash","Nash Ver"],axis=1)

    db = pd.ExcelFile("../database/input/dados.xls")
    basins = db.sheet_names[6:]
    caracUtilizadas = caracFisicas.drop(["Precipitação média - P (mm)","Capacidade de armazenamento do solo CAD (mm)",
                                        "Índice de compacidade da bacia - Kc",],axis=1)
    
    dfCompleted = FormatData(db,basins, caracUtilizadas,pLength,eLength,qLength)


    if args.normalize:
        maxs = dfCompleted.iloc[:,1:-1].max().values
        mins = dfCompleted.iloc[:,1:-1].min().values

        dfCompletedNorm = dfCompleted.copy()
        dfCompletedNorm.iloc[:,1:-1] = dfCompleted.iloc[:,1:-1].apply(lambda x: (x-mins)/(maxs-mins),axis=1)

        dfCompletedNorm.to_csv(os.path.join(path,fileName),index=False)

        MaxMins = pd.DataFrame([maxs,mins], columns=dfCompleted.columns[1:-1])
        MaxMins.to_csv(os.path.join(path,"maxmin_%s.csv"  % fileName))
        print("File Created!")

    else:
        dfCompleted.to_csv(os.path.join(path,fileName),index=False)
        print("File Created!")

if __name__ == "__main__":
    main()





    




