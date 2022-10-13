"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

# Yumeng Jin (yj225) Miracle Zhang (lz284)
# 7 December 2021
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    Attribute: animator is the indicator of coroutine animation
    Invariant: animator is None or an animation function

    Attribute: lifeReducer is the indicator of player losing life
    Invariant: lifeReducer is a boolean statement that is True or False

    Attribute: winner is the indicator of player winning the game
    Invariant: winner is a boolean statement that is True or False

    Attribute: touchline is the indicator of aliens touching the dline
    Invariant: touchline is a boolean statemetn that is True or False
    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    # Attribute _direction: the current moving direction of the matter
    # Invariant: _direction is a boolean statement that is True or False
    #
    # Attribute _playerBolt: the current player bolt
    # Invariant: _playerBolt is a 1-d list of Bolt object
    #
    # Attribute _boltrate: the steps for aliens to shoot waves
    # Invariant: _boltrate is an int between 1 and BOLT_RATE
    #
    # Attribute _stepsshot: the steps after one shot
    # Invariant: _stepsshot is an int larger than 0
    #
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self, bolts = [], lives = SHIP_LIVES, time = 0,
                direction = True):
        """
        Initializes the wave of the game.

        Assigns values to all the hidden class attribute in the game about ship,
        aliens, bolts, and the basic setting.

        Parameter bolts: a list of bolt objects either from the ship or from the
                         aliens
        Parameter lives: number of lives the ship have, with number of SHIP_LIVES
                         when the game starts
        Parameter time: the amount of time passed since the last alien step
        Parameter direction: current moving direction of the aliens. True if
                             the aliens are moving towards the right.
        """
        self._ship = Ship()
        self.fillAlien()
        self._bolts = bolts
        self._dline = GPath(linewidth = 10,
                            points = [0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
                            linecolor = "black")
        self._lives = lives
        self._time = time
        self._direction = direction
        self._playerBolt = []
        self._boltrate = random.randint(1, BOLT_RATE)
        self._stepsshot = 0
        self.animator = None
        self.lifeReducer = False
        self.winnner = False
        self.touchline = False


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        """
        updates the object wave in each frame

        Parameter input: the user input from the command
        Parameter dt: The time in seconds since last update
        """
        if not self.animator is None:
            try:
                self.animator.send(dt)
            except StopIteration:
                self._ship = None
                self._bolts.clear()
        else:
            self.determineWin()
            self.determineLine()
            self.shipInput(input)
            self.fillBolt(input)
            self.removeBolt()
            self.BoltHMove()
            self.alienFire()
            self.determineAlienCollides()
            self.determineShipCollides(dt)
            self.changeDirection(dt)
            self.alienHMove(dt)


    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the game objects to view

        This methods draws GObjects including alien waves, ship, bolts, and
        dline on the screen.
        This method updates at each frame to enable the animation.

        Parameter view: the view of the game used in drawing
        Invariant: view is an object of class GView (from GameApp)
        """
        self._dline.draw(view)
        for i in range(len(self._aliens)):
            for j in range(len(self._aliens[i])):
                if self._aliens[i][j] != None:
                    self._aliens[i][j].draw(view)
        if self._ship != None:
            self._ship.draw(view)
        for i in range(len(self._bolts)):
            if self._bolts[i] != None:
                self._bolts[i].draw(view)


    # HELPER METHODS FOR COLLISION DETECTION
    def fillAlien(self):
        """
        Creates rows of aliens using corresponding images

        Each row of aliens has a corrsponding image. This method loops over
        all alien objects in rows and assign the related images to them.
        """
        height = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_HEIGHT / 2)
        width = ALIEN_H_SEP + (ALIEN_WIDTH / 2)
        listAliens = [ [ [] for j in range(ALIENS_IN_ROW)] for i in range (ALIEN_ROWS)]
        for i in range(ALIEN_ROWS):
            y_pos = height - i * (ALIEN_HEIGHT + ALIEN_V_SEP)
            for j in range(ALIENS_IN_ROW):
                x_pos = width + j * (ALIEN_WIDTH + ALIEN_H_SEP)
                if i == 0:
                    listAliens[i][j] = Alien(x = x_pos, y = y_pos, source = 'alien3.png')
                elif i == 1 or i == 2:
                    listAliens[i][j] = Alien(x = x_pos, y = y_pos, source = 'alien2.png')
                else:
                    listAliens[i][j] = Alien(x = x_pos, y = y_pos, source = 'alien1.png')
        self._aliens = listAliens


    def shipInput(self, input):
        """
        Updates the ship position at each frame.

        Through input, this method check the user key press and move the ship
        in corrsponding direction (either left or right)
        The movement cannot exceed the width of the game window.

        Parameter input: input of the ship
        Invariant: input in an GInput object
        """
        if self._ship != None:
            if input.is_key_down('left') and self._ship.x > 0:
                self._ship.x -= SHIP_MOVEMENT
            if input.is_key_down('right') and self._ship.x < GAME_WIDTH:
                self._ship.x += SHIP_MOVEMENT


    def alienHMove(self, dt):
        """
        Animates the movement of the alien wave.

        The movement of aliens are at the speed determined by the constant
        ALIEN_SPEED

        This method loops over every alien objects in a wave and animates all of
        them in the same direction determined by the attribute self._direction.
        If hidden attribute self._direction is true, the movement of aliens is
        towards right. Otherwise, the movement of aliens is towards the left.

        Parameter dt: Number of frames passed since the last animation frame
        Precondition: dt is an int or float >=0
        """
        if self._time >= ALIEN_SPEED:
            self._time = 0
            self._stepsshot += 1
            if self._direction:
                for i in range(len(self._aliens)):
                    for j in range(len(self._aliens[i])):
                        if self._aliens[i][j] != None:
                            self._aliens[i][j].x += ALIEN_H_WALK
            else:
                for i in range(len(self._aliens)):
                    for j in range(len(self._aliens[i])):
                        if self._aliens[i][j] != None:
                            self._aliens[i][j].x -= ALIEN_H_WALK
        else:
            self._time += dt


    def changeDirection(self, dt):
        """
        Changes the moving direction of the aliens as they hit the boundary.

        This method alters the aliens' direction to right if they were moving
        towards the left before hitting the boundary. Otherwise, it changes the
        aliens' direction to left.

        Parameter dt: Number of seconds passed since the last animation frame
        Precondition: dt is an int or float >=0
        """
        mindistance = 10000
        if self._direction:
            for i in range(ALIENS_IN_ROW):
                for j in range(ALIEN_ROWS):
                    if self._aliens[ALIEN_ROWS-1-j][ALIENS_IN_ROW-1-i] != None:
                        distance = GAME_WIDTH - self._aliens[ALIEN_ROWS-1-j][ALIENS_IN_ROW-1-i].x
                        if distance < mindistance:
                            mindistance = distance
            if mindistance < ALIEN_H_SEP:
                self._direction = False
                for i in range(ALIEN_ROWS):
                    for j in range(ALIENS_IN_ROW):
                        if self._aliens[i][j] != None:
                            self._aliens[i][j].x -= ALIEN_H_SEP - mindistance
                            self._aliens[i][j].y -= ALIEN_V_SEP
        elif not self._direction:
            for i in range(ALIENS_IN_ROW):
                for j in range(ALIEN_ROWS):
                    if self._aliens[j][i] != None:
                        distance = self._aliens[j][i].x
                        if distance < mindistance:
                            mindistance = distance
            if mindistance < ALIEN_H_SEP:
                self._direction = True
                for i in range(ALIEN_ROWS):
                    for j in range(ALIENS_IN_ROW):
                        if self._aliens[i][j] != None:
                            self._aliens[i][j].x += mindistance
                            self._aliens[i][j].y -= ALIEN_V_SEP


    def fillBolt(self, input):
        """
        Reads user keyboard input and create the correspond player bolt.

        Parameter input: the user input from the command
        """
        pewSound1 = Sound('pew1.wav')
        blastS1= Sound('blast1.wav')
        if self._playerBolt == []:
            if input.is_key_down('space') or input.is_key_down('up'):
                if self._ship != None:
                    newBolt = Bolt(self._ship.x, self._ship.y +
                              (SHIP_HEIGHT + BOLT_HEIGHT) / 2)
                    self._playerBolt.append(newBolt)
                    self._bolts.append(newBolt)
                    pewSound1.play()


    def removeBolt(self):
        """
        Removes a bolt from the Attribute _bolts and _playerBolt if out of bound.

        This method compares the current position of the bolts with the window
        boundary of the game to determine and remove the bolts that move out
        of the boundary.
        """
        i = 0
        while i < len(self._bolts):
            if self._bolts[i].y > GAME_HEIGHT - BOLT_HEIGHT / 2:
                    del self._bolts[i]
                    self._playerBolt = []
            elif self._bolts[i].y < BOLT_HEIGHT / 2:
                if self._bolts[i] not in self._playerBolt:
                    del self._bolts[i]
            else:
                i += 1


    def BoltHMove(self):
        """
        Animates the bolt to move according to its velocity.

        This method loops over every single bolts and creates their motion by
        plusing the velocity to it.
        """
        for i in self._bolts:
            i.y += i.velocity


    def alienFire(self):
        """
        Randomly selects one alien to fire the bolt.

        This method first the uses the imported method random.randint() to
        randomly select a row and column number, and animate the corresponding
        alien to shoot the bolt.
        """
        if self._stepsshot == self._boltrate:
            generated = False
            while generated == False:
                i = random.randint(0, ALIEN_ROWS - 1)
                j = random.randint(0, ALIENS_IN_ROW - 1)
                if self._aliens[i][j] != None:
                    newBolt = Bolt(self._aliens[i][j].x, self._aliens[i][j].y,
                                    velocity = - BOLT_SPEED)
                    self._bolts.append(newBolt)
                    generated = True
            self._boltrate = random.randint(1, BOLT_RATE)
            self._stepsshot = 0


    def determineAlienCollides(self):
        """
        Determines and removes the colliding bolt and alien.

        This method loops over every single existing aliens and checks whether
        they collides with a bolt shot by the player. If so, removes both the
        bolts from the player and the alien being shot from the screen.
        Stop the for loop after the removal is done.
        """
        for j in range(len(self._aliens)):
            for k in range (len(self._aliens[j])):
                if self._aliens[j][k] != None:
                    for i in range(len(self._bolts)):
                        if self._bolts[i] in self._playerBolt:
                            if self._aliens[j][k].collides(self._bolts[i]):
                                self._aliens[j][k] = None
                                del self._bolts[i]
                                self._playerBolt = []
                        break


    def determineShipCollides(self, dt):
        """
        Determines and removes the colliding bolt and ship.

        This method loops over every existing alien bolts and checks whether
        they collides with the ship. If so, removes both the
        bolts from the Attribute _bolts and the ship from the screen.
        Stop the for loop after the removal is done.
        """
        if self._ship != None:
            for i in range(len(self._bolts)):
                if self._bolts[i] not in self._playerBolt:
                    if self._ship.collides(self._bolts[i]):
                        self.animator = self.ship_blow()
                        next(self.animator)
                        del self._bolts[i]
                        self._lives -= 1
                        self.lifeReducer = True
                break


    def ship_blow(self):
        """
        Blow up the ship in animation.

        This method is a coroutine that receives and draws multiple images to
        show an animation. It takes dt as its imput value every time it runs,
        which shows the number of time/frames it need to run

        """
        blastS1= Sound('blast1.wav')
        alive = True
        t = 0
        DEATH_SPEED = 1
        while alive:
            dt = (yield)
            t = t + dt
            self._ship.frame = round((t/DEATH_SPEED)*8)
            if self._ship.frame >= 7:
                alive = False
        blastS1.play()
        self.animator = None


    def determineWin(self):
        """
        Determines whether the aliens has been cleared adn the user win.

        This methos loops over all the alien objects on the screen, assigns True
         to the Attribute winner if all of them are cleared, false otherwise.
        The game ends after the user is determined to be the winner.
        """
        determiner = True
        for j in range(len(self._aliens)):
            for k in range (len(self._aliens[j])):
                if self._aliens[j][k] != None:
                    determiner = False
        self.winner = determiner


    def determineLine(self):
        """
        Determines whether the aliens has touched the DEFENSE LINE.

        This method loops over all the alien objects to check whether any of
        them touches the defense line. It assigns True to Attribute touchline if
        dline is reached, False otherwise.
        The game ends after one of the aliens touched the dline. The user loses
        the game.
        """
        determiner = False
        for j in range(len(self._aliens)):
            for k in range (len(self._aliens[j])):
                if self._aliens[j][k] != None:
                    if self._aliens[j][k].y <= DEFENSE_LINE:
                        determiner = True
        self.touchline = determiner
