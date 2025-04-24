import java.util.Scanner;
import java.util.Random;
import java.util.HashMap;
import java.util.Map;
import org.json.JSONObject;





//Compile with
//javac -cp ".:json.jar" AgentJava.java
//or with 
//javac -cp ".;json.jar" AgentJava.java
//if you are on windows






public class AgentJava {
    private static final Random random = new Random();
    
    public static JSONObject makeMove(JSONObject fighterInfo, JSONObject opponentInfo, JSONObject savedData) {
        JSONObject action = new JSONObject();
        action.put("move", JSONObject.NULL);
        action.put("attack", JSONObject.NULL);
        action.put("jump", false);
        action.put("dash", JSONObject.NULL);
        action.put("saved_data" , savedData);
        action.put("debug", "Debug");


        
        
        //Get distance to opponent;
        int distance = Math.abs(fighterInfo.getInt("x") - opponentInfo.getInt("x"));

        // Decide jumping (random with higher chance when opponent is attacking)
        if (opponentInfo.getBoolean("attacking") && random.nextDouble() < 0.6) {
            action.put("jump", true);
        } else if (random.nextDouble() < 0.1) {  // Occasionally jump
            action.put("jump", true);
        }

        // Decide movement
        if (distance > 150) {  // If too far, move towards opponent
            if (fighterInfo.getInt("x") < opponentInfo.getInt("x")) {
                action.put("move", "right");
            } else {
                action.put("move", "left");
            }
        } else if (distance < 80) {  // If too close, back away occasionally
            if (random.nextDouble() < 0.4) {
                if (fighterInfo.getInt("x") < opponentInfo.getInt("x")) {
                    action.put("move", "left");
                } else {
                    action.put("move", "right");
                }
            }
        }

        // Decide attack based on distance and cooldown
        if (distance < 200 && !fighterInfo.getBoolean("attacking") && 
            fighterInfo.getInt("attack_cooldown") == 0) {
            if (distance < 120 && random.nextDouble() < 0.7) {
                action.put("attack", random.nextDouble() < 0.5 ? 1 : 2);
            } else if (random.nextDouble() < 0.3) {
                action.put("attack", random.nextDouble() < 0.5 ? 1 : 2);
            }
        }

        // Decide dashing
        if (distance < 100 && opponentInfo.getBoolean("attacking") && random.nextDouble() < 0.5) {
            if (fighterInfo.getInt("x") < opponentInfo.getInt("x")) {
                action.put("dash", "left");
            } else {
                action.put("dash", "right");
            }
        }

        return action;
    }
    
    public static void main(String[] args) {
        try {
            // Read input JSON from stdin
            Scanner scanner = new Scanner(System.in);
            String input = scanner.nextLine();
            scanner.close();
            
            JSONObject data = new JSONObject(input);
            JSONObject fighterInfo = data.getJSONObject("fighter");
            JSONObject opponentInfo = data.getJSONObject("opponent");
            JSONObject savedData = data.getJSONObject("saved_data");
            
            // Get move decision
            JSONObject move = makeMove(fighterInfo, opponentInfo,savedData);
            
            // Output the move as JSON
            System.out.println(move.toString());
            // System.out.println("nicely done");
            
        } catch (Exception e) {
            JSONObject defaultMove = new JSONObject();
            defaultMove.put("move", JSONObject.NULL);
            defaultMove.put("attack", JSONObject.NULL);
            defaultMove.put("jump", false);
            defaultMove.put("dash", JSONObject.NULL);
            System.out.println(defaultMove.toString());
            System.err.println("Error: " + e.getMessage());
        }
    }
}
