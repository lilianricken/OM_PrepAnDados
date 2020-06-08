package Classifier;

import weka.classifiers.trees.RandomForest;
import weka.core.DenseInstance;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ConverterUtils;

import java.io.*;

public class RFClassifier {
    public String RandomForestClassifier() throws Exception {

        String alerta = "off";

        ConverterUtils.DataSource dsTreino = new ConverterUtils.DataSource("baseTreinamento.csv");
        Instances insTreino = dsTreino.getDataSet();

        insTreino.setClassIndex(6);

        RandomForest randomForest = new RandomForest();
        randomForest.setBatchSize("100");
        randomForest.setBreakTiesRandomly(true);

        randomForest.buildClassifier(insTreino);

        File file = new File("media.csv");
        try (
                FileReader fileReader = new FileReader(file);
                BufferedReader bufferedReader = new BufferedReader(fileReader)) {

            String line = bufferedReader.readLine();

            while (line != null) {
                String[] colunas = line.split(";");

                Instance insMedia = new DenseInstance(7);

                insMedia.setDataset(insTreino);
                insMedia.setValue(0, Double.parseDouble(colunas[1]));
                insMedia.setValue(1, Double.parseDouble(colunas[2].replaceAll(",", ".")));
                insMedia.setValue(2, Double.parseDouble(colunas[3]));
                insMedia.setValue(3, Double.parseDouble(colunas[4]));
                insMedia.setValue(4, Double.parseDouble(colunas[5].replaceAll(",", ".")));
                insMedia.setValue(5, Double.parseDouble(colunas[6].replaceAll(",", ".")));

                double[] probabilidade = randomForest.distributionForInstance(insMedia);
                boolean StatusAlerta = false;

                //@attribute Classe {frio,alerta,quente,moderado}
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
