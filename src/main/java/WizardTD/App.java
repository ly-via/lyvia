package WizardTD;

import processing.core.PApplet;
import processing.core.PImage;
import processing.data.JSONArray;
import processing.data.JSONObject;
import processing.event.MouseEvent;

import java.awt.Graphics2D;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;

import java.io.*;
import java.util.*;
import processing.core.*;

/**
 * App class extends PApplet
 * perform the overall operations of the game
 */
public class App extends PApplet {
    public static final int FPS = 60;
    public static final int TOPBAR = 40;
    public static final int SIDEBAR = 120;
    public static final int CELLSIZE = 32;
    public static final int CELLCENTERED = CELLSIZE / 2;
    public static final int WIZARDSIZE = 48;
    public static final int BOARD_WIDTH = 20;
    public static final int WIDTH = CELLSIZE*BOARD_WIDTH+SIDEBAR;
    public static final int HEIGHT = BOARD_WIDTH*CELLSIZE+TOPBAR;
    public static final int GRASSLOC = 0;
    public static final int SHURBLOC = 1;
    public static final int PATHLOC = 2;
    public static final int WALLLOC = 3;
    public static final int WIZARDHOUSELOC = 9;
    public static final int BUTTON_Y = 50; // buttons' y locations
    public static final int BUTTON_HEIGHT = 40;
    public static final int BUTTON_WIDTH = SIDEBAR - 85;
    public static final int BUTTON_X = BOARD_WIDTH*CELLSIZE+10; // buttons' x locations
    public static final int[][] BOARD = new int[20][BOARD_WIDTH]; // set board size

    public int[] wizardHouseXY;
    public String configPath, type;
    public Random random = new Random();
    public PImage grass, shrub, path0, path1, path2, path3,
                  tower0, tower1, tower2, wizardHouse, fireballPic,
                  monsterType, gremlin, beetle, worm, gremlin1,
                  gremlin2, gremlin3, gremlin4, gremlin5, wall;

    public char tile;
    public PFont fonts;
    public Fireball fireball;
    public JSONObject loadJSON;
    public JSONArray WAVES, MONSTERS;
    public PVector towerClickedLOC = null;

    public ArrayList<PVector> locForTowers = new ArrayList<>();
    public ArrayList<Monster> monsterSpawn = new ArrayList<>();
    // https://stackoverflow.com/questions/39698472/processing-tower-defence-game-towers-attacking-enemies
    public ArrayList<Fireball> fireballs = new ArrayList<Fireball>();

    public float prewave, iniTowerFiringSpeed, MPScapMul, MPSmanaGainedMul, minDistance,
                 dx, dy, armour, speed, FFspeed = 1.0f, Xpos, Ypos;
    // for monster & wave
    public int preWavePauseCounter, waveDurationCounter, duration, maxQuantity,
               totalFrames, framePerMonster, newCost, totalCost,
               hp, mana_gained, quantity, initialMana_gained, countDown,
               currentMONS = 0, currentWAVE = -1, maxDeathAni = 5;
    // for tower & mana pool spell
    public int iniTowerRange, iniTowerDamage, iniMana, currentMana, iniManaCap,
               iniManaPerSec, towerCost, MPSiniCost, MPScostIncrease,
               newUpgradeCost, newRangeCost, newSpeedCost, newDamageCost,
               usedMPSonce, upgradeCost = 20, eachUpCost = 10,
               upRangeLevel, upSpeedLevel, upDamageLevel;
    public boolean allWithinUpgradeLevel = upRangeLevel <= 3 &&
                                            upSpeedLevel <= 3 &&
                                            upDamageLevel <= 3;

    private int frameCounter;
    public PImage[] deathAnimations = new PImage[maxDeathAni];
    public boolean Paused = false, FastForward = false, buildTowerClick = false,
                   towerBuilt = false, isUpgradeRange = false, isUpgradeDamage = false,
                   isUpgradeSpeed = false, towerClicked = false, gameLost = false,
                   overButton, withinBudget, allLevelTWO, atLeastAllLevelONE, atLeastAllLevelTWO;

    public App() {
        this.configPath = "config.json";
    }

    /**
     * Initialise the setting of the window size.
     */
    @Override
    public void settings() { size(WIDTH, HEIGHT); }

    /**
     * Load all resources such as images. Initialise the elements such as the player, enemies and map elements.
     * Source: https://forum.processing.org/two/discussion/10137/different-font-versions-light-ultrabold-etc-other-than-italic-bold-don-t-show-in-processing.html
     * Source 2: http://learningprocessing.com/examples/chp15/example-15-03-ImageArray1
     */
    @Override
    public void setup() {
        frameRate(FPS);
        size(WIDTH, HEIGHT); // board layout dimension
        fonts = createFont("Calibri Bold", 25);
        textFont(fonts);
        // Load images
        wall = loadImage("src/main/resources/WizardTD/wall.png");
        grass = loadImage("src/main/resources/WizardTD/grass.png");
        shrub = loadImage("src/main/resources/WizardTD/shrub.png");
        path0 = loadImage("src/main/resources/WizardTD/path0.png");
        path1 = loadImage("src/main/resources/WizardTD/path1.png");
        path2 = loadImage("src/main/resources/WizardTD/path2.png");
        path3 = loadImage("src/main/resources/WizardTD/path3.png");
        tower0 = loadImage("src/main/resources/WizardTD/tower0.png");
        tower1 = loadImage("src/main/resources/WizardTD/tower1.png");
        tower2 = loadImage("src/main/resources/WizardTD/tower2.png");
        fireballPic = loadImage("src/main/resources/WizardTD/fireball.png");
        wizardHouse = loadImage("src/main/resources/WizardTD/wizard_house.png");
        worm = loadImage("src/main/resources/WizardTD/worm.png");
        beetle = loadImage("src/main/resources/WizardTD/beetle.png");
        gremlin = loadImage("src/main/resources/WizardTD/gremlin.png");
        gremlin1 = loadImage("src/main/resources/WizardTD/gremlin1.png");
        gremlin2 = loadImage("src/main/resources/WizardTD/gremlin2.png");
        gremlin3 = loadImage("src/main/resources/WizardTD/gremlin3.png");
        gremlin4 = loadImage("src/main/resources/WizardTD/gremlin4.png");
        gremlin5 = loadImage("src/main/resources/WizardTD/gremlin5.png");
        // reference to Source 2
        deathAnimations[0] = gremlin1;
        deathAnimations[1] = gremlin2;
        deathAnimations[2] = gremlin3;
        deathAnimations[3] = gremlin4;
        deathAnimations[4] = gremlin5;
        loadConfigFile();
    }

    /**
     * Load and read JSON config file
     * and match tiles on game board with the layout text file given.
     * Source 1: https://stackoverflow.com/questions/45185839/how-to-get-array-from-json-object
     * Source 2: https://processing.org/reference/JSONObject_getJSONArray_.html
     */
    public void loadConfigFile() {
        try {
            // load JSON file
            loadJSON = loadJSONObject(this.configPath);
            String readLayout = loadJSON.getString("layout");
            String[] layout = loadStrings(readLayout); // read layout txt file

            int rows = layout.length;
            int cols = layout[0].length();

            iniTowerRange = loadJSON.getInt("initial_tower_range");
            iniTowerFiringSpeed = loadJSON.getFloat("initial_tower_firing_speed");
            iniTowerDamage = loadJSON.getInt("initial_tower_damage");
            iniMana = loadJSON.getInt("initial_mana");
            currentMana = iniMana;
            iniManaCap = loadJSON.getInt("initial_mana_cap");
            iniManaPerSec = loadJSON.getInt("initial_mana_gained_per_second");
            towerCost = loadJSON.getInt("tower_cost");
            MPSiniCost = loadJSON.getInt("mana_pool_spell_initial_cost");
            MPScostIncrease = loadJSON.getInt("mana_pool_spell_cost_increase_per_use");
            MPScapMul = loadJSON.getFloat("mana_pool_spell_cap_multiplier");
            MPSmanaGainedMul = loadJSON.getFloat("mana_pool_spell_mana_gained_multiplier");

            // reference to source 1 and 2
            WAVES = loadJSON.getJSONArray("waves");
            startNextWave();

            // match tiles on game board
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    if (j < layout[i].length()) {
                        tile = layout[i].charAt(j);
                        // match tiles & images
                        if (tile == 'S') { BOARD[i][j] = SHURBLOC; }
                        else if (tile == 'X') { BOARD[i][j] = PATHLOC; }
                        else if (tile == 'W') { BOARD[i][j] = WIZARDHOUSELOC; }
                        else if (tile == 'A') { BOARD[i][j] = WALLLOC; }
                        else if (tile == ' ') { BOARD[i][j] = GRASSLOC; }
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Error with JSON" + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Load wave's properties from JSON file.
     * Source: https://stackoverflow.com/questions/25346512/read-multiple-objects-json-with-java
     * @param waveIndex For getting the next wave while reading the config file
     */
    public void readWave(int waveIndex) {
        // reference to source
        if (waveIndex < WAVES.size()) {
            JSONObject wavesProperty = WAVES.getJSONObject(waveIndex);
            duration = wavesProperty.getInt("duration");
            prewave = wavesProperty.getFloat("pre_wave_pause");

            MONSTERS = wavesProperty.getJSONArray("monsters");
            currentMONS = 0;  // reset monster to 1st wave
            readMonster(currentMONS);
        }
        countDown = duration + (int)(prewave) * FPS;
    }

    /**
     * Load monster's properties from JSON file.
     * Source 1: https://stackoverflow.com/questions/25346512/read-multiple-objects-json-with-java
     * Source 2: https://www.codingninjas.com/studio/library/what-are-conditional-statements-in-java
     * Source 3: https://www3.ntu.edu.sg/home/ehchua/programming/java/JavaGame_TicTacToe.html
     * @param monsterIndex For getting the next monster properties
     */
    public void readMonster(int monsterIndex) {
        // reference to source 1
        if (monsterIndex < MONSTERS.size()) {
            JSONObject monsterProperty = MONSTERS.getJSONObject(monsterIndex);

            type = monsterProperty.getString("type");
            hp = monsterProperty.getInt("hp");
            speed = monsterProperty.getFloat("speed");
            armour = monsterProperty.getFloat("armour");
            mana_gained = monsterProperty.getInt("mana_gained_on_kill");
            initialMana_gained = mana_gained;
            quantity = monsterProperty.getInt("quantity");

            if (type.equals("gremlin")) {
                monsterType = gremlin;
            } else if (type.equals("worm")) {
                monsterType = worm;
            } else if (type.equals("beetle")) {
                monsterType = beetle;
            }
            totalFrames = duration * FPS;
            // reference to source 2 and 3
            // (condition) ? (return if true) : (return if false);
            framePerMonster = (quantity != 0) ? totalFrames / quantity : totalFrames;
            maxQuantity = 0;
        }
    }

    /**
     * Proceed the game for next wave.
     * Source: https://www.youtube.com/watch?v=C4_iRLlPNFc&amp;t=7252s&amp;ab_channel=ChrisCourses
     */
    public void startNextWave() {
        currentWAVE++;
        if (currentWAVE < WAVES.size()) {
            readWave(currentWAVE);
            // reference to source
            waveDurationCounter = duration * FPS;
            preWavePauseCounter = Math.round(prewave * FPS);
        }
    }

    /**
     * Build tower if there is empty grass and deduct the cost
     * @param x X coordinate for the tower to be placed
     * @param y Y coordinate for the tower to be placed
     */
    public void buildTower(int x, int y) {
        if (currentMana >= towerCost) {
            if (isEmptyGrass(x, y)) {
                // get the loactions for empty grass
                int centerX = x - CELLCENTERED;
                int centerY = y - CELLCENTERED;
                locForTowers.add(new PVector(centerX, centerY));
                currentMana -= towerCost;
            }
        }
    }

    /**
     * Convert mouse pressed position to grid.
     * Source: https://stackoverflow.com/questions/55527159/how-to-convert-the-mouse-position-in-pixels-into-the-row-and-column-on-the-grid
     * @param mouseX X coordinate of the mouse
     * @param mouseY Y coordinate of the mouse
     * @return int array for converted grid coordinates of the mouse
     */
    public int[] convertMouseClick(int mouseX, int mouseY) {
        int gridX = mouseX / CELLSIZE;
        int gridY = (mouseY - TOPBAR) / CELLSIZE;
        return new int[]{gridX, gridY};
    }

    /**
     * Check available empty grass spaces to build tower.
     * Source 1: https://happycoding.io/tutorials/processing/collision-detection
     * Source 2: https://stackoverflow.com/questions/40759783/detect-location-of-known-points-in-a-rectangle
     * @param mouseX X coordinate of the mouse
     * @param mouseY Y coordinate of the mouse
     * @return boolean result if mouse positions are on empty grass for building towers
     */
    public boolean isEmptyGrass(int mouseX, int mouseY) {
        int[] topLeft = convertMouseClick(mouseX, mouseY); // top-left
        int[] bottomRight = convertMouseClick(mouseX+CELLSIZE, mouseY+CELLSIZE); // bottom-right

        for (int i = topLeft[1]; i <= bottomRight[1]; i++) {
            for (int j = topLeft[0]; j <= bottomRight[0]; j++) {
                if (!isGrassCheck(i, j)) {
                    return false; // not empty grass
                }
            }
        }
        return true; // empty grass for placing towers
    }

    /**
     * Check the board for only grass tiles.
     * @param i X grid of the empty grass space on board
     * @param j Y grid of the empty grass space on board
     * @return boolean result if the grid on the board is empty grass
     */
    public boolean isGrassCheck(int i, int j) {
        // loop through the entire board
        if(i < BOARD.length && j < BOARD[i].length)
            if (BOARD[i][j] == GRASSLOC) { // check only grass
                return true;
        }
        return false;
    }

    /**
     * Check and display the yellow circle range around the hovered tower.
     */
    public void drawYellowCircle_hovered() {
        PVector isHoverOverTower = getTowerLOC_hovered();
        if (towerBuilt && (isUpgradeRange || isUpgradeSpeed || isUpgradeDamage)) {
            if (!(isHoverOverTower == null)) {
                stroke(255, 255, 0); // yellow border
                strokeWeight(2);
                noFill();
                ellipse(isHoverOverTower.x+CELLCENTERED, isHoverOverTower.y+CELLCENTERED, iniTowerRange*2, iniTowerRange*2);
            }
        }
    }

    /**
     * Check and display the upgrade cost table for selected upgrades for the hovered tower.
     */
    public void showUpgradedCostTableifHovered() {
        PVector isHoverOverTower = getTowerLOC_hovered();
        if (towerBuilt && (isUpgradeRange || isUpgradeSpeed || isUpgradeDamage)) {
            if (!(isHoverOverTower == null)) {
                // draw table header
                fill(255);        // white box
                stroke(color(0)); // black border
                strokeWeight(1);  // border width
                rect(BUTTON_X, 560, 76, 20);

                // -- table header text
                fill(0);
                textSize(12);
                textAlign(LEFT, CENTER);
                text("Upgrade cost", BUTTON_X + 3, 570);

                // draw content table
                fill(255);
                stroke(color(0));
                strokeWeight(1);
                rect(BUTTON_X, 580, 76, 50);

                // -- content text
                fill(0);
                textSize(12);
                textAlign(LEFT, CENTER);
                newCost = calculateUpgradeCost();
                totalCost = 0;

                if (isUpgradeRange) {
                    totalCost += newCost;
                    text("range:         " + newCost, BUTTON_X + 3, 590);
                }
                if (isUpgradeSpeed) {
                    totalCost += newSpeedCost;
                    text("speed:        " + newCost, BUTTON_X + 3, 605);
                }
                if (isUpgradeDamage) {
                    totalCost += newCost;
                    text("damage:    " + newCost, BUTTON_X + 3, 620);
                }
                // draw total table
                fill(255);
                stroke(color(0));
                strokeWeight(1);
                rect(BUTTON_X, 630, 76, 18);

                // -- total text
                fill(0);
                textSize(12);
                textAlign(LEFT, CENTER);
                text("Total:          " + totalCost, BUTTON_X + 3, 640);
            }
        }
    }

    /**
     * Calculate the new upgrade cost with the maximum upgrade levels.
     * @return int for the updated cost after upgrades selected
     */
    public int calculateUpgradeCost() {
        if (allWithinUpgradeLevel) { // upgrade within all max levels
            if (isUpgradeRange) {
                newRangeCost = upgradeCost + upRangeLevel * eachUpCost;
                newUpgradeCost = newRangeCost;
            }
            if (isUpgradeSpeed) {
                newSpeedCost = upgradeCost + upSpeedLevel * eachUpCost;
                newUpgradeCost = newSpeedCost;
            }
            if (isUpgradeDamage) {
                newDamageCost = upgradeCost + upDamageLevel * eachUpCost;
                newUpgradeCost = newDamageCost;
            }
        }
        return newUpgradeCost; }

    /**
     * Get the coordinates of hovered tower.
     * @return PVector for tower locations
     */
    public PVector getTowerLOC_hovered() {
        for (PVector tower : locForTowers) {
            float x = Math.abs(mouseX - tower.x);
            float y = Math.abs(mouseY - tower.y);

            if (x <= CELLCENTERED && y <= CELLCENTERED) {
                return tower; }
        }
        return null; }

    /**
     * Perform fast forward actions and update monster's speed.
     */
    public void setFastForward() {
        if (FastForward) {
            FFspeed = 2;
            for (Monster monster : monsterSpawn) {
                monster.speed = speed * FFspeed;
            }
        } else {
            FFspeed = 1;
            for (Monster monster : monsterSpawn) {
                monster.speed = speed * FFspeed;
            }
        }
    }

    /**
     * Upgrade the initial range of tower with default cell size.
     */
    public void upgradeRange() {
        iniTowerRange += CELLSIZE; // increase by 1 tile = cellsize = 32 pixels
        int newCost = calculateUpgradeCost();
        currentMana -= newCost;  // deduct current mana based on upgrade levels
    }

    /**
     * Upgrade the initial speed of fireball by 0.5 per second increase.
     */
    public void upgradeSpeed() {
        iniTowerFiringSpeed += 0.5; // increase by 0.5 fireballs per second
        int newCost = calculateUpgradeCost();
        currentMana -= newCost;
    }

    /**
     * Upgrade the initial dealth by half initial tower damage.
     */
    public void upgradeDamage() {
        iniTowerDamage += (iniTowerDamage / 2); // increase by 1/2 initial tower damage
        int newCost = calculateUpgradeCost();
        currentMana -= newCost;
    }

    /**
     * Perform mana pool spell actions.
     */
    public void ManaPoolSpellAction() {
        if (currentMana >= MPSiniCost) {
            usedMPSonce += 1;                // get counter for mana pool spell
            currentMana -= MPSiniCost;       // deduct the current mana with cost
            iniManaCap *= MPScapMul;         // increase the total max mana value
            MPSiniCost += usedMPSonce * MPScostIncrease; // increase cost per use
            mana_gained = Math.round(initialMana_gained * usedMPSonce * (1 + (MPSmanaGainedMul - 1)));
        }   // ^ increase mana_gained
    }

    /**
     * Receive key pressed signal from the keyboard.
     * Source 1: https://forum.processing.org/one/topic/start-stop-pause-processing.html
     * Source 2: https://stackoverflow.com/questions/61565143/how-to-pause-and-resume-a-thread-in-java
     */
    @Override
    public void keyPressed() {
        // reference to source 1
        if (key == 'f') {   // speed up monsters
            FastForward = !FastForward;
            setFastForward(); }

        // reference to source 2
        if (key == 'p') {  // pause
            Paused = !Paused; }

        if (key == 't') {  // build tower
            buildTowerClick = !buildTowerClick; }

        if (key == '1') { // upgrade range
            isUpgradeRange = !isUpgradeRange; }

        if (key == '2') {  // upgrade speed
            isUpgradeSpeed = !isUpgradeSpeed; }

        if (key == '3') { // upgrade damage
            isUpgradeDamage = !isUpgradeDamage; }

        if (key == 'm') { // mana pool spell
            ManaPoolSpellAction(); }

        if (key == 'r') { // restart
            currentWAVE = -1; // reset wave
            Paused = false;
            FastForward = false;
            buildTowerClick = false;
            isUpgradeRange = false;
            isUpgradeDamage = false;
            isUpgradeSpeed = false;
            gameLost = false;
            setup();
            monsterSpawn.clear(); // reset monster array
            locForTowers.clear();
        }

        // build tower selected
        if (buildTowerClick) {
            buildTower(mouseX, mouseY); }
    }

    /**
     * Receive key released signal from the keyboard.
     */
    @Override
    public void keyReleased(){ }

    /**
     * Check the position of mouseX to be within the button.
     * @return boolean result if the mouseX is within certain range
     */
    public boolean checkMouseX() {
        return (mouseX >= BUTTON_X && mouseX <= BUTTON_X + BUTTON_WIDTH);
    }

    /**
     * Receive mouse clicked signal.
     * Source 1: https://processing.org/tutorials/interactivity
     * Source 2: https://forum.processing.org/one/topic/start-stop-pause-processing.html
     * Source 3: https://stackoverflow.com/questions/12396066/how-to-get-location-of-a-mouse-click-relative-to-a-swing-window
     * @param e Mouse event
     */
    @Override
    public void mousePressed(MouseEvent e) {
        // reference to source 1
        if (checkMouseX() && mouseY >= BUTTON_Y && // fast forward
            mouseY <= BUTTON_Y + BUTTON_HEIGHT) {
            FastForward = !FastForward;
            setFastForward();
        // reference to source 2
        } else if (checkMouseX() && mouseY >= BUTTON_Y+50 &&  // paused
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+50) {
            Paused = !Paused;

        } else if (checkMouseX() && mouseY >= BUTTON_Y+100 && // build tower
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+100) {
            buildTowerClick = !buildTowerClick;

        } else if (checkMouseX() && mouseY >= BUTTON_Y+150 && // upgrade range
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+150) {
            isUpgradeRange = !isUpgradeRange;

        } else if (checkMouseX() && mouseY >= BUTTON_Y+200 && // upgrade speed
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+200) {
            isUpgradeSpeed = !isUpgradeSpeed;

        } else if (checkMouseX() && mouseY >= BUTTON_Y+250 && // upgrade damage
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+250) {
            isUpgradeDamage = !isUpgradeDamage;

        } else if (checkMouseX() && mouseY >= BUTTON_Y+300 && // mana pool spell
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+300) {
            ManaPoolSpellAction();
        }

        // reference to source 3
        int mouseX = e.getX();
        int mouseY = e.getY();
        // build tower below top bar
        if (!(mouseY <= TOPBAR) && buildTowerClick) {
            buildTower(mouseX, mouseY);
        }

        // AFTER UPGRADE BUTTON SELECTED
        PVector isHoverOverTower = getTowerLOC_hovered();
        if (isHoverOverTower != null) { // tower is hovered
            if (checkTowerClicked(isHoverOverTower)) {
                towerClicked = !towerClicked; // tower is clicked

                if (towerClicked) {
                    towerClickedLOC = isHoverOverTower; }
                 else {
                    towerClickedLOC = null; }
            }

            // PERFORM UPGRADES CHECKING CURRENT MANA & UPGRADE LEVEL
            if (towerClicked) {
                int newCost = calculateUpgradeCost();
                // upgrade within budget
                if (currentMana >= newCost && currentMana > 0) {
                        checkCurrentManaWithinLevels();
                } else { // over budget, upgrade based on hierarchy
                    checkCurrentManaWithinLevels();
                }
            }
        }
    }

    /**
     * Draw tool tip when hovered to build tower and mana pool spell buttons.
     */
    public void drawTooltip() {
        if (checkMouseX() && mouseY >= BUTTON_Y+100 && // build tower button
            mouseY <= BUTTON_Y + BUTTON_HEIGHT+100) {
            fill(255);
            stroke(color(0));
            strokeWeight(1);
            rect(BUTTON_X-65, 150, 50, 18);
            fill(0);
            textSize(12);
            textAlign(CENTER, CENTER);
            text("Cost: 100", BUTTON_X-40, 158);

        } else if (checkMouseX() && mouseY >= BUTTON_Y+300 &&
                   mouseY <= BUTTON_Y + BUTTON_HEIGHT+300) {
            fill(255);
            stroke(color(0));
            strokeWeight(1);
            rect(BUTTON_X-65, 350, 50, 18);
            fill(0);
            textSize(12);
            textAlign(CENTER, CENTER);
            text("Cost: " + MPSiniCost, BUTTON_X-40, 358);
        }
    }

    /**
     * Check which upgrade selection is selected and check if can be performed within budget.
     */
    public void checkCurrentManaWithinLevels() {
        int newCost = calculateUpgradeCost();
        boolean withinBudget = currentMana > 0 && currentMana >= newCost;

        if (isUpgradeRange && withinBudget && upRangeLevel < 3) {
            upgradeRange();
            upRangeLevel += 1; // increment the upgrade times
        }
        if (isUpgradeSpeed && withinBudget && upSpeedLevel < 3) {
            upgradeSpeed();
            upSpeedLevel += 1;
        }
        if (isUpgradeDamage && withinBudget && upDamageLevel < 3) {
            upgradeDamage();
            upDamageLevel += 1;
        }
    }

    /**
     * check if the tower is clicked.
     * @param tower Pvector locations of which tower is clicked
     * @return boolean result if the tower is clicked
     */
    public boolean checkTowerClicked(PVector tower) {
        return mouseX > tower.x &&
               mouseX < tower.x + CELLSIZE &&
               mouseY > tower.y &&
               mouseY < tower.y + CELLSIZE;
    }

    /**
     * Receive mouse release signal.
     * @param e Mouse event
     */
    @Override
    public void mouseReleased(MouseEvent e) { }

    /**
     * Draw all elements in the game by current frame.
     */
    @Override
    public void draw() {
        background(152, 177, 136); // SET BG TO GREEN COLOR

        displayBoard(); // 1. DISPLAY ENTIRE BOARD LAYOUT WITH TILES
        displayWizardHouse();

        drawTowersYellowCircle(); // 2. DRAW TOWER & YELLOW CIRCLE

        TopSideBarsButtons();     // 3. yellow circle under TOP SIDE BAR
        drawTooltip();            // draw tool tips for build tower & mana

        // 4. DRAW & SPAWN MONSTERS
        frameCounter++;
        if (preWavePauseCounter > 0) {
            preWavePauseCounter--;
            return; } // skip the rest of the loop

        if (!Paused && waveDurationCounter > 0) {
            if (framePerMonster != 0 && frameCounter % framePerMonster == 0 &&
                maxQuantity < quantity) {
                spawnMonsters(); // spawn within quantity
            }
            waveDurationCounter--; }

        drawMonsters();

        displayWizardHouse(); // DRAW WIZARD HOUSE on top of monsters

        // 5. DRAW FIREBALLS
        fireballMechanism();
        drawFireballs();

        // INCREASE CURRENT MANA PER SECOND
        if (!Paused && frameCounter % FPS == 0) {
            currentMana += iniManaPerSec;
        }
    }

    Map<PVector, Integer> towerCooldowns = new HashMap<>();

    /**
     * Get locations for the tower and monsters.
     * Source 1: https://stackoverflow.com/questions/7071457/maximum-value-for-float-in-java
     * Source 2: https://processing.org/reference/PVector_dist_.html
     * @param towerLoc Location of tower
     * @return the monsters that are closest to the current checking tower
     */
    public Monster getClosestMonster(PVector towerLoc) {
        // reference to source 1
        minDistance = Float.MAX_VALUE;
        Monster closestMonster = null;

        for (Monster monster : monsterSpawn) {
            // reference to source 2
            float distance = PVector.dist(towerLoc, new PVector(monster.x, monster.y));
            if (!(distance > minDistance)) {
                minDistance = distance;
                closestMonster = monster;
            }
        }
        if (minDistance >= iniTowerRange) {
            return null;
        } else {
            return closestMonster;
        }
    }

    /**
     * Draw tower and yellow circle range for the hovered tower and
     * draw upgrade symbols for range, speed, damage
     */
    public void drawTowersYellowCircle() {
        for (PVector towerLoc : locForTowers) {
            towerBuilt = true;

            if (allWithinUpgradeLevel) {
                drawYellowCircle_hovered(); } // draw yellow circle

                allLevelTWO = upRangeLevel == 2 && upSpeedLevel == 2 && upDamageLevel == 2;
                atLeastAllLevelONE = upRangeLevel >= 1 && upSpeedLevel >= 1 && upDamageLevel >= 1;
                atLeastAllLevelTWO = upRangeLevel >= 2 && upSpeedLevel >= 2 && upDamageLevel >= 2;

                if (!atLeastAllLevelONE) { // default tower
                    image(tower0, towerLoc.x, towerLoc.y);
                } else if (atLeastAllLevelONE && !atLeastAllLevelTWO) { // level 1
                    image(tower1, towerLoc.x, towerLoc.y);
                } else if (atLeastAllLevelTWO) { // level 2
                    image(tower2, towerLoc.x, towerLoc.y);
                }
                // DRAW UPGRADE SYMBOLS
                // RANGE -- 'O' @ top-left
                Xpos = towerLoc.x + 2;
                Ypos = towerLoc.y;
                if (upRangeLevel == 1 && upSpeedLevel != 1 && upDamageLevel != 1) { // level 1
                    drawRangeO(Xpos, Ypos);
                }
                if (upRangeLevel == 2 && upSpeedLevel != 2 && upDamageLevel != 2) {
                    drawRangeO(Xpos, Ypos);
                    drawRangeO(Xpos + 6, Ypos);
                }
                if (upRangeLevel == 3) {
                    drawRangeO(Xpos, Ypos);
                    drawRangeO(Xpos + 6, Ypos);
                    drawRangeO(Xpos + 14, Ypos);
                }

                // DAMAGE -- 'X' @ bottom-left
                float DamageY = Ypos + 28;
                if (upDamageLevel == 1 && upSpeedLevel != 1 && upRangeLevel != 1) { // level 1
                    drawDamageX(Xpos - 3, DamageY);
                }
                if (upDamageLevel == 2 && upSpeedLevel != 2 && upRangeLevel != 2) {
                    drawDamageX(Xpos - 3, DamageY);
                    drawDamageX(Xpos + 4, DamageY);
                }
                if (upDamageLevel == 3) {
                    drawDamageX(Xpos - 3, DamageY);
                    drawDamageX(Xpos + 4, DamageY);
                    drawDamageX(Xpos + 10, DamageY);
                }

                // SPEED -- blue circle @ center
                float speedX = Xpos + 3;
                float speedY = Ypos + 6;
                if (upSpeedLevel == 1 && upDamageLevel != 1 && upRangeLevel != 1) { // level 1
                    strokeWeight(2);
                    drawSpeedRect(speedX, speedY);
                }
                if (upSpeedLevel == 2 && upDamageLevel != 2 && upRangeLevel != 2) { // level 2
                    strokeWeight(3);
                    drawSpeedRect(speedX, speedY);
                }
                if (upSpeedLevel == 3 && !allLevelTWO) { // level 3
                    strokeWeight(4);
                    drawSpeedRect(speedX, speedY);
                }
            }
    }

    /**
     * Draw fireballs and check if the fireballs hit the monster.
     */
    public void drawFireballs() {
        for (int i = fireballs.size() - 1; i >= 0; i--) {
            if (!Paused) {
                Fireball fb = fireballs.get(i);

                if (fb.hasHitTarget(this)) {
                    fireballs.remove(i); }
                fb.shootFireball(this);
                fb.drawFireball(this); }
        }
    }

    /**
     * Draw monsters and check the death status of each monsters,
     * and track the game win or lose status.
     * Source 1: https://stackoverflow.com/questions/74736965/how-to-start-pause-and-stop-thread-in-java-in-proper-way
     * Source 2: http://learningprocessing.com/examples/chp15/example-15-03-ImageArray1
     */
    public void drawMonsters() {
        boolean spawnedDone = true;

        for (int i = monsterSpawn.size() - 1; i >= 0; i--) {
            Monster monster = monsterSpawn.get(i);

            if (monster.isActive) {  // check available monsters to spawn
                spawnedDone = false; // continue spawning the monsters
                // reference to source 1
                if (!Paused) {
                    monster.spawnMonster(this);
                }
                monster.draw(this);
                monster.drawHPBar(this);

                if (!monster.isAlive && !Paused) { // monsters are killed
                    if (monster.deathAniIndex < deathAnimations.length) {
                        // reference to source 2
                        image(deathAnimations[monster.deathAniIndex], monster.x, monster.y);
                        if (frameCounter % maxDeathAni == 0) { // lasting 4 frames
                            monster.deathAniIndex++; }
                    } else {
                        currentMana += mana_gained; // +currentMana with mana on killed
                        monsterSpawn.remove(i);  }  // kill them
                }
            } else { // remove from the board when reach wizard house
                monsterSpawn.remove(i); }

            // check if banishment cost (currentHP) > currentMana
            if (monster.reachedWizardHouse(this) && monster.currentHP > currentMana) {
                gameLost = true; }
        }
        if (gameLost) { // lose the game
            textAlign(CENTER, CENTER);
            textSize(30);
            fill(78,232,97,255);
            text("YOU LOST\nPress 'r' to restart", 325, 233);
            Paused = true;
        } else {
            if (monsterSpawn.size() == 0){
                textAlign(CENTER, CENTER);
                textSize(40);
                fill(255, 0, 255);
                text("YOU WIN", 325, 240);
            }
        }

        if (currentWAVE < WAVES.size() && currentWAVE > 2) { // start next wave
            if (waveDurationCounter <= 0 && spawnedDone) {
                startNextWave(); }
        }
    }

    /**
     * Manage the fireball operations and control the speed.
     * Source: https://www.geeksforgeeks.org/hashmap-getordefaultkey-defaultvalue-method-in-java-with-examples/
     */
    public void fireballMechanism() {
        for (PVector towerLoc : locForTowers) {
            if (allWithinUpgradeLevel) {
                showUpgradedCostTableifHovered();
            }
            // reference to source
            int cooldown = towerCooldowns.getOrDefault(towerLoc, 0);
            if (cooldown != 0) {
                towerCooldowns.put(towerLoc, cooldown - 1);
            } else {
                Monster closestMonster = getClosestMonster(towerLoc);
                if (closestMonster != null) {
                    PVector closestMonsterPos = new PVector(closestMonster.x, closestMonster.y);
                    int towerX = (int)(towerLoc.x);
                    int towerY = (int)(towerLoc.y);
                    int monsX = (int)(closestMonsterPos.x);
                    int monsY = (int)(closestMonsterPos.y);
                    Fireball newFireball = new Fireball(towerX, towerY, monsX, monsY, fireballPic, closestMonster);
                    fireballs.add(newFireball);
                    towerCooldowns.put(towerLoc, FPS);
                }
            }
        }
    }

    /**
     * Display entire board layout with corresonding image for each tiles.
     * Source: https://www.w3schools.com/java/java_switch.asp
     */
    public void displayBoard() {
        for (int i = 0; i < BOARD.length; i++) {
            for (int j = 0; j < BOARD[i].length; j++) {
                // Reference to source
                switch (BOARD[i][j]) {
                    case GRASSLOC:
                        image(grass, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        break;
                    case WALLLOC:
                        image(wall, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        break;
                    case SHURBLOC:
                        image(shrub, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        break;
                    case PATHLOC:
                        String getPaths = matchPaths(j, i);
                        // horizontal straight
                        if (getPaths.equals("horizontal straight")) {
                            image(path0, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("vertical straight")) { // vertical straight
                            PImage result = rotateImageByDegrees(path0, 90.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("cross")) {
                            image(path3, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        // T-junctions
                        } else if (getPaths.equals("up left right")) {
                            PImage result = rotateImageByDegrees(path2, 180.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("down left right")) {
                            image(path2, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("up down left")) {
                            PImage result = rotateImageByDegrees(path2, 90.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("up down right")) {
                            PImage result = rotateImageByDegrees(path2, 270.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        // corner paths
                        } else if (getPaths.equals("below right corner")) {
                            PImage result = rotateImageByDegrees(path1, 270.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("below left corner")) {
                            image(path1, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("above right corner")) {
                            PImage result = rotateImageByDegrees(path1, 90.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else if (getPaths.equals("above left corner")) {
                            PImage result = rotateImageByDegrees(path1, 90.0);
                            image(result, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        } else {
                            image(path0, j * CELLSIZE, i * CELLSIZE + TOPBAR);
                        }
                        break;
                }
            }
        }
    }

    /**
     * Display wizard house after resizing and centered to the tile.
     */
    public void displayWizardHouse() {
        for (int i = 0; i < BOARD.length; i++) {
            for (int j = 0; j < BOARD[i].length; j++) {
                if (BOARD[i][j] == WIZARDHOUSELOC) {
                    int wizardX = j * CELLSIZE;
                    int wizardY = (i * CELLSIZE + TOPBAR / 2) + 10;
                    wizardHouseXY = new int[]{wizardX, wizardY};
                    wizardHouse.resize(48, 48);
                    image(wizardHouse, wizardX, wizardY);
                }
            }
        }
    }

    /**
     * Draw top bar, mana slide bar, side bar and buttons.
     * Source: https://processing.org/reference/text_.html
     */
    public void TopSideBarsButtons() {
        fill(132, 115, 74); // TOP BAR
        noStroke();         // remove top bar border
        rect(0, 0, WIDTH, TOPBAR); // display top bar

        fill(132, 115, 74); // SIDE BAR
        noStroke();         // remove side bar border
        rect(WIDTH - SIDEBAR, 0, SIDEBAR, HEIGHT); // display side bar

        // BUTTONS
        drawButton("FF", BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, FastForward);
        drawButton("P",  BUTTON_X, BUTTON_Y+50, BUTTON_WIDTH, BUTTON_HEIGHT, Paused);
        drawButton("T",  BUTTON_X, BUTTON_Y+100, BUTTON_WIDTH, BUTTON_HEIGHT, buildTowerClick);
        drawButton("U1", BUTTON_X, BUTTON_Y+150, BUTTON_WIDTH, BUTTON_HEIGHT, isUpgradeRange);
        drawButton("U2", BUTTON_X, BUTTON_Y+200, BUTTON_WIDTH, BUTTON_HEIGHT, isUpgradeSpeed);
        drawButton("U3", BUTTON_X, BUTTON_Y+250, BUTTON_WIDTH, BUTTON_HEIGHT, isUpgradeDamage);
        drawButton("M",  BUTTON_X, BUTTON_Y+300, BUTTON_WIDTH, BUTTON_HEIGHT, false);

        // TOP BAR TEXT
        textSize(30);
        textAlign(LEFT, CENTER);
        int waveText = TOPBAR - 30;
        int startText = TOPBAR + 70;

        if (countDown > 0) {
            countDown--; } // count down

        int countdownSec = countDown / FPS;

        String topbarWaveText = "Wave " + (currentWAVE + 2);
        text(topbarWaveText, waveText, 15);
        String topbarStartText = "starts: " + countdownSec;
        text(topbarStartText, startText, 15);

        // mana slide text box
        textSize(23);
        textAlign(LEFT, CENTER);
        int manaText = TOPBAR + 270;
        text("MANA:", manaText, 18);

        // mana slide white box
        int slidebarWidth = 335, barHeight = 22;
        stroke(color(0)); // black border
        fill(255);        // white bg text box
        strokeWeight(2);  // black border width
        rect(manaText + 75, 10, slidebarWidth, barHeight); // white slide bar

        // mana slide aqua box
        int aquabarWidth = Math.round((float)currentMana / iniManaCap * slidebarWidth);
        stroke(color(0));
        fill(0, 255, 255); // aqua bg
        strokeWeight(3);
        rect(manaText + 75, 10, aquabarWidth, barHeight);

        // text inside slide bar
        textSize(20);
        fill(0); // black text color
        text(currentMana + " / " + iniManaCap, manaText + 200, 20);

        // SIDE BAR TEXT
        textSize(14);
        textAlign(LEFT, CENTER);
        int sidetextX = BUTTON_X + BUTTON_WIDTH + 6;   // x location
        int sidetextY = BUTTON_Y + BUTTON_WIDTH / 2;   // y locations
        // reference to source
        text("2x speed", sidetextX, sidetextY);
        text("PAUSE", sidetextX, sidetextY + 50);
        text("Build\ntower", sidetextX, sidetextY + 100);
        text("Upgrade\nrange", sidetextX, sidetextY + 150);
        text("Upgrade\nspeed", sidetextX, sidetextY + 200);
        text("Upgrade\ndamage", sidetextX, sidetextY + 250);
        text("Mana pool\ncost: " + MPSiniCost, sidetextX, sidetextY + 300);
    }

    /**
     * Draw magenta 'O' at top-left of tower for range upgrade.
     * @param x X coordinate of the tower selected
     * @param y Y coordinate of the tower selected
     */
    public void drawRangeO(float x, float y) {
        int newCost = calculateUpgradeCost();
        stroke(255, 0, 255); // magenta color
        strokeWeight(2);
        noFill();
        ellipse(x, y, 8, 8); // circle shape
    }

    /**
     * Draw magenta 'X' at bottom-left of tower for damage upgrade.
     * @param x X coordinate of the tower selected
     * @param y Y coordinate of the tower selected
     */
    public void drawDamageX(float x, float y) {
        int newCost = calculateUpgradeCost();
        textSize(12);
        fill(255, 0, 255); // magenta color
        text("X", x, y);
    }

    /**
     * Draw blue rectangle with different border thickness for speed upgrade.
     * @param x X coordinate of the tower selected
     * @param y Y coordinate of the tower selected
     */
    public void drawSpeedRect(float x, float y) {
        int newCost = calculateUpgradeCost();
        stroke(123, 181, 255, 255); // blue color
        noFill();
        PVector isHoverOverTower = getTowerLOC_hovered();
        rect(x, y, 20, 20);
    }

    /**
     * Spawn the monsters by adding new monsters to the game.
     * Source: https://gamedev.stackexchange.com/questions/82572/enemy-spawning-problem
     */
    public void spawnMonsters() {
        if (currentMONS < MONSTERS.size()) {
            if (maxQuantity < quantity) { // spawn within quantity
                ArrayList<PVector> path = generatePath();
                if (!path.isEmpty()) {
                    PVector point = path.get(0);
                    dx = point.x;
                    dy = point.y;
                    float newSpeed = speed * FFspeed; // update new speed
                    // reference to source
                    Monster monster = new Monster(this, monsterType, hp, newSpeed, armour, dx, dy, mana_gained, quantity, path);
                    monsterSpawn.add(monster); // add monster obj to arraylist
                    maxQuantity++; }
            } else { // get next property
                currentMONS++;
                maxQuantity = 0; }
        } else { // get next wave
            currentWAVE++;
            currentMONS = 0;
            maxQuantity = 0; }
    }

    /**
     * Check validity of path within the board.
     * Source: https://www.geeksforgeeks.org/shortest-path-in-a-binary-maze/
     * @param y Y location of the entry point of the path
     * @param x X location of the entry point of the path
     * @return boolean result if the path is valid
     */
    public boolean isValidPath(int y, int x) {
        return y >= 0 && y < BOARD.length && x >= 0 && x < BOARD[0].length;
    }

    /**
     * Get the coordinates of available path with matching each of the tiles on board.
     * Source 1: https://gamedev.stackexchange.com/questions/43347/how-to-handle-frame-rates-and-synchronizing-screen-repaints
     * Source 2: https://medium.com/geekculture/breadth-first-search-in-java-d32d29f6bb9e
     * Source 3: https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
     * Source 4: https://www.programiz.com/dsa/graph-bfs
     * Source 5: https://www.geeksforgeeks.org/check-possible-path-2d-matrix/
     * Source 6: https://www.geeksforgeeks.org/shortest-path-in-a-binary-maze/
     * Source 7: https://forum.processing.org/two/discussion/2829/fifo-queue-problem-with-code.html
     * @return Array list of PVector containing the locations of the valid path.
     */
    public ArrayList<PVector> generatePath() {
        ArrayList<PVector> path = new ArrayList<>();
        Queue<PVector> queue = new LinkedList<>(); // reference to source 7
        PVector startPoint = getSpawnPoint();

        // reference to source 1
        int gridX = (int)(startPoint.x / CELLSIZE);
        int gridY = (int)((startPoint.y - TOPBAR) / CELLSIZE);
        queue.add(startPoint);

        // reference to source 2
        boolean[][] visited = new boolean[BOARD.length][BOARD[0].length];
        visited[gridY][gridX] = true;

        // reference to source 3 and 4
        while(queue.size() != 0) {
            PVector current = queue.poll();
            path.add(current);

            // reference to source 5
            int[][] directions = {{0,1}, {1,0}, {0,-1}, {-1,0}};
            for(int[] dir : directions) {
                int newY = (int)(current.y - TOPBAR) / CELLSIZE + dir[0];
                int newX = (int)current.x / CELLSIZE + dir[1];

                // reference to source 6
                if(isValidPath(newY, newX) && BOARD[newY][newX] == PATHLOC && !visited[newY][newX]) {
                    queue.add(new PVector(newX * CELLSIZE + 5, newY * CELLSIZE + TOPBAR + 5));
                    visited[newY][newX] = true; }
            }
        }
        return path; }

    /**
     * Get the starting point of the path for the monsters to spawn on the board.
     * Source 1: https://itecnote.com/tecnote/java-tic-tac-toe-game-java-using-only-methods-and-2d-arrays/
     * Source 2: https://coderanch.com/t/706724/java/Tic-Tac-Toe-GetWinner-method
     * @return Pvector of the entry point for the monsters to start.
     */
    public PVector getSpawnPoint() {
        // reference to source 1
        // left and right columns for path entry
        for (int i = 0; i < BOARD.length; i++) {
            if (BOARD[i][0] == PATHLOC) {
                return new PVector(5, i*CELLSIZE+TOPBAR+5);
            }
            if (BOARD[i][BOARD[i].length - 1] == PATHLOC) {
                return new PVector((BOARD[i].length - 1)*CELLSIZE+5, i*CELLSIZE+TOPBAR+5);
            }
        }
        // top and bottom rows for path entry
        for (int j = 0; j < BOARD[0].length; j++) {
            if (BOARD[0][j] == PATHLOC) {
                return new PVector(j*CELLSIZE+5, 5);
            }
            // reference to source 2
            if (BOARD[BOARD.length - 1][j] == PATHLOC) {
                return new PVector(j*CELLSIZE+5, (BOARD.length - 1) *CELLSIZE+TOPBAR+5);
            }
        }
        return null;
    }

    /**
     * Identify the types of path, junctions with each of the tiles on the board.
     * Source: https://www.geeksforgeeks.org/multidimensional-arrays-in-java/
     * @param x X location on the board tile to be matched
     * @param y Y location on the board tile to be matched
     * @return Short description of the current path
     */
    public String matchPaths(int x, int y) {
        int left = -1, right = -1, above = -1, below = -1;

        // reference to source
        if (x > 0) { left = BOARD[y][x-1]; }
        if (x < BOARD[x].length - 1) { right = BOARD[y][x+1]; }
        if (y > 0) { above = BOARD[y-1][x]; }
        if (y < BOARD.length - 1) { below = BOARD[y+1][x]; }

        // cross-junction path
        if (left == PATHLOC && right == PATHLOC && above == PATHLOC && below == PATHLOC) {
            return "cross";
        // T-junction path
        } else if (above == PATHLOC && left == PATHLOC && right == PATHLOC) {
            return "up left right";
        } else if (below == PATHLOC && left == PATHLOC && right == PATHLOC) {
            return "down left right";
        } else if (above == PATHLOC && below == PATHLOC && left == PATHLOC) {
            return "up down left";
        } else if (above == PATHLOC && below == PATHLOC && right == PATHLOC) {
            return "up down right";
        // straight path (HORIZONTAL)
        } else if (left == PATHLOC && right == PATHLOC) {
            return "horizontal straight";
        // straight path (VERTICAL)
        } else if (above == PATHLOC && below == PATHLOC) {
            return "vertical straight";
        // corner path
        } else if (below == PATHLOC && right == PATHLOC) {
            return "below right corner";
        } else if (below == PATHLOC && left == PATHLOC) {
            return "below left corner";
        } else if (above == PATHLOC && right == PATHLOC) {
            return "above right corner";
        } else if (above == PATHLOC && left == PATHLOC) {
            return "above left corner";
        } else if (above == PATHLOC) {
            return "vertical straight";   // VERTICAL
        } else if (below == PATHLOC) {
            return "vertical straight";   // VERTICAL
        } else {
            return "straight"; // HORIZONTAL
        }
    }

    /**
     * Draw button for the side bar.
     * Source 1: https://discourse.processing.org/t/change-color-with-click-or-touch/31295/6
     * Source 2: https://processing.org/reference/color_.html
     * Source 3: https://processing.org/reference/PFont.html
     * @param label Text to be written to the buttons
     * @param x X position of the button
     * @param y Y position of the button
     * @param w Width of the button
     * @param h Height of the button
     * @param clicked Boolean result if the specific button is clicked
     */
    public void drawButton(String label, float x, float y, float w, float h, boolean clicked) {
        overButton = mouseX >= x && mouseX <= x + w &&
                             mouseY >= y && mouseY <= y + h;

        if (overButton && !clicked) {
            fill(206, 206, 206);  // grey color when hover
        } else if (clicked) {
            fill(255, 255, 0);
        } else {
            fill(132, 115, 74); } // default brown color

        rect(x, y, w, h); // display buttons size
        stroke(color(0)); // border with black color
        strokeWeight(2);  // border width
        noFill();         // not filling buttons with colors
        rect(x, y, w, h); // display border

        textAlign(LEFT, CENTER);
        textSize(25);
        fill(0);                   // black font color
        text(label, x+4, y+h / 2); // button label fonts
    }

    public static void main(String[] args) {
        PApplet.main("WizardTD.App");
    }

    /**
     * Source: https://stackoverflow.com/questions/37758061/rotate-a-buffered-image-in-java
     * @param pimg The image to be rotated
     * @param angle between 0 and 360 degrees
     * @return the new rotated image
     */
    public PImage rotateImageByDegrees(PImage pimg, double angle) {
        BufferedImage img = (BufferedImage) pimg.getNative();
        double rads = Math.toRadians(angle);
        double sin = Math.abs(Math.sin(rads)), cos = Math.abs(Math.cos(rads));
        int w = img.getWidth();
        int h = img.getHeight();
        int newWidth = (int) Math.floor(w * cos + h * sin);
        int newHeight = (int) Math.floor(h * cos + w * sin);

        PImage result = this.createImage(newWidth, newHeight, RGB);
        //BufferedImage rotated = new BufferedImage(newWidth, newHeight, BufferedImage.TYPE_INT_ARGB);
        BufferedImage rotated = (BufferedImage) result.getNative();
        Graphics2D g2d = rotated.createGraphics();
        AffineTransform at = new AffineTransform();
        at.translate((newWidth - w) / 2, (newHeight - h) / 2);

        int x = w / 2;
        int y = h / 2;

        at.rotate(rads, x, y);
        g2d.setTransform(at);
        g2d.drawImage(img, 0, 0, null);
        g2d.dispose();
        for (int i = 0; i < newWidth; i++) {
            for (int j = 0; j < newHeight; j++) {
                result.set(i, j, rotated.getRGB(i, j));
            }
        }
        return result;
    }
}