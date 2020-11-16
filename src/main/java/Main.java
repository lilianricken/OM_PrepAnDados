import Classifier.JRipClassifier;
import javamqtt.ClienteMQTT;

public class Main {

    public static void main(String[] args) throws Exception {
        ClienteMQTT clienteMQTT = new ClienteMQTT("tcp://broker.hivemq.com:1883",
                null, null);
        clienteMQTT.iniciar();

        JRipClassifier jRip = new JRipClassifier();

        while (true) {
            String alerta = jRip.RandomForestClassifier();
            clienteMQTT.publicar("PUCPR/OMIoT/A85DE0A994EEEED17BD0229875B5F585/alerta/",
                    alerta.getBytes(), 0);
        }
    }
}