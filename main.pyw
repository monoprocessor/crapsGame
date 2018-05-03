#! /usr/bin/env python
__author__ = 'Daniel Purcell'

from die import * 
import sys, logging
from PyQt5 import QtGui, uic
from pickle import load, dump
from PyQt5.QtWidgets import  QMainWindow, QApplication, QDialog, QMessageBox

class Craps(QMainWindow) :
    """A game of Craps."""
    die1 = die2 = None

    def __init__( self, parent=None ):
        """Build a game with two dice."""
        logging.info("Game started")

        super().__init__(parent)

        self.quitCounter = 0  # used in a workaround for a QT5 Bug.

        uic.loadUi("Craps.ui", self)

        self.bidSpinBox.setRange ( 10, 100 )
        self.bidSpinBox.setSingleStep ( 5 )
        self.resultText = "You have not rolled yet."
        self.payouts = {4: 2, 5: 1.5, 6: 1.2, 8: 1.2, 9: 1.5, 10: 1.2}
        self.bailButton.setEnabled(False)

        try:
            with open('craps.pkl', 'rb') as crapsLol:
                stuff = load(crapsLol)
                print(stuff)
                self.wins, self.losses, self.bank, self.resultText, self.total = stuff

        except:
            self.wins = 0
            self.losses = 0
            self.bank = 1000
            self.resultText = "WELCOME TO CRAPS"

        self.logging = True
        self.die1 = Die()
        self.die2 = Die()
        self.minimumBet = 1
        self.maximumBet = 1000
        self.startingBank = 1000
        self.total = 0
        self.firstRoll = True

        self.buttonText = "Roll"
             #          0  1  2  3  4    5    6    7    8    9    10   11   12
        self.payouts = [0, 0, 0, 0, 2.0, 1.5, 1.2, 1.0, 1.2, 1.5, 2.0, 1.0, 0]
        if self.logging:
            logging.info("Rolled")

            self.updateUI()

        self.rollButton.clicked.connect(self.rollButtonClickedHandler)
        self.bailButton.clicked.connect(self.bail)
        self.restartButton.clicked.connect(self.restart)
        self.settingsBtn.clicked.connect(self.showSettings)

    def showSettings(self):
        settings.show()
        if self.logging:
            logging.info("Settings opened.")

    def restart(self):
        self.wins = 0
        self.losses = 0
        self.firstRoll = True
        self.bank = self.startingBank
        self.resultText = "Game restarted."
        self.updateUI()

        if self.logging:
            logging.info("You just restarted the game")

    def bail(self):
        self.resultText = "Bailed."
        self.firstRoll = True
        self.updateUI()
        self.bailButton.setEnabled(False)
        self.rollingForLabel.setText("Bailed.")
        if self.logging:
            logging.info("You just bailed")


    def __str__( self ):
        """String representation for Dice.
        """

        return "Die1: %s\nDie2: %s" % ( str(self.die1),  str(self.die2) )

    def updateUI ( self ):
        self.die1View.setPixmap(QtGui.QPixmap( ":/" + str( self.die1.getValue() ) ) )
        self.die2View.setPixmap(QtGui.QPixmap( ":/" + str( self.die2.getValue() ) ) )
        self.rollingForLabel.setText("Your roll is " + str(self.total))
        self.winsLabel.setText(str(self.wins))
        self.lossesLabel.setText(str(self.losses))
        self.resultsLabel.setText(str(self.resultText))
        self.bankValue.setText("$" + str(self.bank))
        # Add your code here to update the GUI view so it matches the game state.

		# Player asked for another roll of the dice.
    def rollButtonClickedHandler ( self ):
        self.currentBet = self.bidSpinBox.value()

        if self.currentBet > self.bank:
            self.resultText = "You do not have enough money."
            self.updateUI()
            return

        if self.currentBet > self.maximumBet:
            self.resultText = "This bet is too high"
            self.updateUI()
            return

        if self.currentBet < self.minimumBet:
            self.resultText = "This bet is too low."
            self.updateUI()
            return

        self.die1.roll()
        self.die2.roll()
        self.total = self.die1.getValue() + self.die2.getValue()

        if self.firstRoll:
            if self.total == 7 or self.total == 11:
                self.resultText = "You win!"
                self.wins += 1
                self.bank += self.currentBet
            elif self.total == 2 or self.total == 3:
                self.resultText = "You lose."
                self.losses += 1
                self.bank -= self.currentBet
            else:
                self.firstRoll = False
                self.resultText = "Roll again."
                self.bailButton.setEnabled(True)
                self.previousRolled = self.total

        else:
            self.bailButton.setEnabled(False)
            if self.total == self.previousRolled:
                self.resultText = "You win!"
                self.wins += 1
                self.bank += self.payouts[self.total] * self.currentBet
            else:
                self.resultText = "You lose."
                self.losses += 1
                self.bank -= self.currentBet
            self.firstRoll = True

        if self.bank <= 0:
            self.resultText = "Game Over"
            self.rollButton.setEnabled(False)
        self.updateUI()

    def closeEvent(self, event):
        quit_msg = "Would you like to save and exit?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        self.pickleInfo = [self.wins, self.losses, self.bank, self.resultText, self.total]

        if reply == QMessageBox.Yes:
            event.accept()
            with open("craps.pkl", 'wb') as crapsPickle:
                dump(self.pickleInfo, crapsPickle)
            exit()
        else:
            event.ignore()
        if self.logging:
            logging.info("Game saved")

class Settings(QDialog):
    def __init__( self, parent=None ):
        """Build a game with two dice."""

        super().__init__(parent)
        uic.loadUi("Settings.ui", self)

        self.buttonBox.accepted.connect(self.saveSettings)

    def saveSettings(self):
        diceApp.startingBank = self.startingBankDefault.value()
        diceApp.minimumBet = self.minimumBetDefault.value()
        diceApp.maximumBet = self.maximumBetDefault.value()
        print(diceApp.maximumBet)
        if diceApp.logging:
            logging.info("Pressed settings button")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logger = logging.basicConfig(filename='craps.log', level=logging.INFO,
                                 format='%(asctime)s %(levelname)s Ln %(lineno)d: %(message)s',
                                 datefmt='%m/%d/%Y %I:%M:%S %p')
    diceApp = Craps()
    diceApp.updateUI()
    diceApp.show()
    settings = Settings()
    sys.exit(app.exec_())


