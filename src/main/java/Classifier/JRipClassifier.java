package Classifier;

import weka.classifiers.rules.JRip;
import weka.classifiers.trees.RandomForest;
import weka.core.DenseInstance;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ConverterUtils;

import java.io.*;

public class JRipClassifier {
    public String RandomForestClassifier() throws Exception {

        String alerta = "off";

        ConverterUtils.DataSource dsTreino = new ConverterUtils.DataSource("baseTreino.csv");
        Instances insTreino = dsTreino.getDataSet();

        insTreino.setClassIndex(6);

        JRip jRip = new JRip();

        jRip.buildClassifier(insTreino);

        File file = new File("newAccess.csv");
        try (
                FileReader fileReader = new FileReader(file);
                BufferedReader bufferedReader = new BufferedReader(fileReader)) {

            String line = bufferedReader.readLine();

            while (line != null) {
                String[] colunas = line.split(",");

                Instance insPcap = new DenseInstance(11);

                insPcap.setDataset(insTreino);
                insPcap.setValue(0, Double.parseDouble(colunas[0])); //Timestamp
                insPcap.setValue(1, colunas[1]); //SourceIP
                insPcap.setValue(2, colunas[2]); //DestinationIP
                insPcap.setValue(3, Double.parseDouble(colunas[3])); //SourcePort
                insPcap.setValue(4, Double.parseDouble(colunas[4])); //DestinationPort
                insPcap.setValue(5, Double.parseDouble(colunas[5])); //FirstAckTimestamp
                insPcap.setValue(6, Double.parseDouble(colunas[6])); //FinTimestamp
                insPcap.setValue(7, Double.parseDouble(colunas[7])); //TotalLength
                insPcap.setValue(8, Double.parseDouble(colunas[8])); //PacketsFromServer
                insPcap.setValue(9, Double.parseDouble(colunas[9])); //PacketsPerTotalTime
                insPcap.setValue(10, colunas[10]); //DOS
                double[] probabilidade = jRip.distributionForInstance(insPcap);
                boolean StatusAlerta = false;

                //@attribute Classe {ataque, normal}
                for (double probabilidadeClasse : probabilidade) {
                    StatusAlerta = probabilidade[1] >= probabilidadeClasse;
                }

                if (StatusAlerta = true) {
                    alerta = "on";
                }

                line = bufferedReader.readLine();
            }
        } catch (
                FileNotFoundException e) {
            System.out.println("File not found");
        } catch (
                IOException e) {
            System.out.println("Problem Reading the file" + file.getName());
        }
        return alerta;
    }
}
