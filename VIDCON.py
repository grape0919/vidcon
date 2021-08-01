import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
from PyQt5 import uic

import numpy as np
import static.staticValues as staticValues
import cv2

from view import main
from pathlib import Path
import time
#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
#form_class = uic.loadUiType("view/main.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, main.Ui_MainWindow) :
    _filePath = ""
    def __init__(self) :
        super(WindowClass, self).__init__()
        self.setupUi(self)
        #메인 화면 색상py
        self.setStyleSheet("color: black;"
                        "background-color: white")
        
        #버튼 스타일 변경
        self.openFileButton.setStyleSheet(staticValues.buttonStyleSheet)
        self.openFileButton.setFont(staticValues.buttonFont)
        self.openFileButton.clicked.connect(self.showFileDialog)

        #영상 편집 버튼
        self.applyButton.setStyleSheet(staticValues.buttonStyleSheet)
        self.applyButton.setFont(staticValues.buttonFont)
        self.applyButton.clicked.connect(self.convertVideo)

        #가로/세로 입력창
        self.horizontalEdit.setValidator(QIntValidator(1, 10000, self))
        self.verticalEdit.setValidator(QIntValidator(1, 10000, self))

        #옵션 버튼
        self.addOptionCheckBox.stateChanged.connect(self.addOptionStateChanged)
        self.addOptionCheckBox.setChecked(False)

        self.exceptOptionCheckBox.setChecked(False)

    def showFileDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open video', 'Desktop',
                                            "Movies (*.avi *.mp4)")
        if fname[0]:
            self._filePath = fname[0]
            self.outputFilePath = str(Path(self._filePath).parent)+'/stretched_output.mp4'
            self.filePathEdit.setText(fname[0])
            
            self.videoFileCV = cv2.VideoCapture(self.filePathEdit.text())

            if not self.videoFileCV.isOpened():
                QMessageBox.about(self, "Warning", "해당파일을 열 수 없습니다.")
                

            self.width = int(self.videoFileCV.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.videoFileCV.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.originFps = round(self.videoFileCV.get(cv2.CAP_PROP_FPS))
            self.fileFpsLabel.setText(str(int(self.originFps)))
            
            self.horizontalEdit.setText(str(self.width))
            self.verticalEdit.setText(str(self.height))
            #TODO FPS 도 label로 표시
        else:
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")
            self.filePathEdit.setText("")
            self.fileFpsLabel.setText("")
            self.horizontalEdit.setText("")
            self.verticalEdit.setText("")

    def checkVideoSize(self):
        print("changeFilePath")

    def convertVideo(self):
        if not self.filePathEdit.text():
            QMessageBox.about(self, "Warning", "파일을 선택하지 않았습니다.")

        fourcc = cv2.VideoWriter_fourcc(*'DIVX')

        changeHeight = self.verticalEdit.text()
        changeWidth = self.horizontalEdit.text()
        
        if self.addOptionCheckBox.isChecked() and int(self.originFps) != 60:
            QMessageBox.about(self, "Warning", "고급편집은 FPS가 60hz인 영상만 편집이 가능합니다.")
            return        
            
        
        print("resizing start")

        self.videoFileCV = cv2.VideoCapture(self.filePathEdit.text())
        pgDialog = QProgressDialog("","Cancel",0, int(self.videoFileCV.get(cv2.CAP_PROP_FRAME_COUNT)))
        pgDialog.setWindowTitle("Editing....")
        pgDialog.canceled.connect(self.progressCancel)
        self.progressing = True
        i = 0

        pgDialog.setValue(i)
        ### resizing setting
        pgDialog.setLabelText("resize setting...")
        retio = self.getRatio(self.height, self.width, int(changeHeight), int(changeWidth))
        # 변환 행렬, X축으로, Y축으로 이동   
        if(retio[1]==int(changeHeight)): #Width 가 같을때
            move = np.float32([[1,0,(int(changeWidth)-retio[0])/2],[0,1,0]])
        elif(retio[0]==int(changeWidth)):
            move = np.float32([[1,0,0],[0,1,(int(changeHeight)-retio[1])/2]])
        # 회전 설정    
        # rota = cv2.getRotationMatrix2D((int(changeWidth)/2, int(changeHeight)/2), self.rotation, 1)

        ### stretch setting
        pgDialog.setLabelText("stretch setting...")
        if self.addOptionCheckBox.isChecked() and self.fps120Radio.isChecked():
            out = cv2.VideoWriter(self.outputFilePath, fourcc, 120, (int(changeWidth),
                    int(changeHeight)))
        else :
            out = cv2.VideoWriter(self.outputFilePath, fourcc, 60, (int(changeWidth),
                    int(changeHeight)))

        # videoWriter 생성
        
        # out = cv2.VideoWriter(self.outputFilePath, fourcc, self.originFps, (int(changeWidth),
        #                         int(changeHeight)))

        out.set(cv2.CAP_PROP_FRAME_WIDTH,int(changeWidth))
        out.set(cv2.CAP_PROP_FRAME_HEIGHT,int(changeHeight))

        pgDialog.setLabelText("editing...")
        temp = np.uint8(np.arange(self.height*self.width*3).reshape(self.height, self.width, 3))
        
        temp.fill(0)

        # 프레임 크기 변경
        temp = cv2.resize(temp, dsize=retio, interpolation=cv2.INTER_LINEAR)
        temp = cv2.warpAffine(temp, move,(int(changeWidth), int(changeHeight)))
        # print(temp.shape, temp.dtype)
        # temp = cv2.integral(temp)\
        while(self.videoFileCV.isOpened()):
            if not self.progressing:
                out.release()
                QMessageBox.about(self, "Warning", "파일 편집을 중단하였습니다.\n작업파일을 삭제합니다.")
                os.remove(self.outputFilePath)
                break

            ret2, frame2 = self.videoFileCV.read()

            if ret2 == False:
                break
            ### resizing
            # 프레임 크기 변경
            temp2 = cv2.resize(frame2, dsize=retio, interpolation=cv2.INTER_LINEAR)
            # 프레임을 가운데로 이동
            temp2 = cv2.warpAffine(temp2, move,(int(changeWidth), int(changeHeight)))
            # 프레임을 회전
            # temp2 = cv2.warpAffine(temp2, rota, (int(changeWidth), int(changeHeight)))
            
            # cv2.imshow("2", temp2)

            ############
            # stripe
            genFrame = temp

            if self.addOptionCheckBox.isChecked() and self.optionStripeRadio.isChecked():
                genFrame[:, 1::2] = temp2[:, 1::2]
                out.write(genFrame)

            elif self.addOptionCheckBox.isChecked() and self.optionZigzag1Radio.isChecked():
                genFrame[::2, ::2] = temp2[::2, ::2]
                genFrame[1::2, 1::2] = temp2[1::2, 1::2]
                out.write(genFrame)

            elif self.addOptionCheckBox.isChecked() and self.optionZigzag2Radio.isChecked():
                for idx in range(int(changeHeight)):
                    mod = idx%4
                    if mod == 0 or mod == 1:
                        genFrame[idx, ::2] = temp2[idx, ::2]
                    elif mod == 2 or mod == 3:
                        genFrame[idx, 1::2] = temp2[idx, 1::2]
                
                out.write(genFrame)


            # 디버그용 미리보기
            # cv2.imshow("2", genFrame)
            # cv2.imshow("3", temp2)
            # QMessageBox.about(self, "DEBUG 확인", "DEBUG 확인")
            
            if self.addOptionCheckBox.isChecked() and not self.exceptOptionCheckBox.isChecked():
                out.write(temp2)

            temp = temp2

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # PROGRESS 증가
            i+=1
            pgDialog.setValue(i)
            # time.sleep(0.3)

        # cv2.destroyAllWindows()

        if self.progressing:
            QMessageBox.about(self, "Succeed", "파일 편집이 완료되었습니다.")
        self.videoFileCV.release()
        out.release()

        print("resizing end")

    def progressCancel(self):
        self.progressing = False
        
    def getRatio(self, originHeight, originWidth, changeHeight, changeWidth):
        tempHeight = (originHeight / originWidth) * changeWidth
        if(tempHeight > changeHeight):
            tempWidth = (originWidth / originHeight) * changeHeight
            return (int(tempWidth), int(changeHeight))
        else:
            return (int(changeWidth), int(tempHeight))

    def addOptionStateChanged(self):
        if not self.addOptionCheckBox.isChecked():
            self.editOptionLabel.setStyleSheet(staticValues.disabledStyleSheet)
            self.FPSLabel.setStyleSheet(staticValues.disabledStyleSheet)

            self.optionStripeRadio.setStyleSheet(staticValues.disabledStyleSheet)
            self.optionStripeRadio.setEnabled(False)
            self.optionStripeRadio.setChecked(True)

            self.optionZigzag1Radio.setStyleSheet(staticValues.disabledStyleSheet)
            self.optionZigzag1Radio.setEnabled(False)

            self.optionZigzag2Radio.setStyleSheet(staticValues.disabledStyleSheet)
            self.optionZigzag2Radio.setEnabled(False)

            self.fps60Radio.setStyleSheet(staticValues.disabledStyleSheet)
            self.fps60Radio.setEnabled(False)
            self.fps60Radio.setChecked(True)

            self.fps120Radio.setStyleSheet(staticValues.disabledStyleSheet)
            self.fps120Radio.setEnabled(False)

            self.OptionsLabel.setStyleSheet(staticValues.disabledStyleSheet)

            self.exceptOptionCheckBox.setStyleSheet(staticValues.disabledStyleSheet)
            self.exceptOptionCheckBox.setChecked(False)
            self.exceptOptionCheckBox.setEnabled(False)
        else:
            self.editOptionLabel.setStyleSheet(staticValues.enabledStyleSheet)
            self.FPSLabel.setStyleSheet(staticValues.enabledStyleSheet)

            self.optionStripeRadio.setStyleSheet(staticValues.enabledStyleSheet)
            self.optionStripeRadio.setChecked(False)
            self.optionStripeRadio.setEnabled(True)

            self.optionZigzag1Radio.setStyleSheet(staticValues.enabledStyleSheet)
            self.optionZigzag1Radio.setChecked(False)
            self.optionZigzag1Radio.setEnabled(True)

            self.optionZigzag2Radio.setStyleSheet(staticValues.enabledStyleSheet)
            self.optionZigzag2Radio.setChecked(False)
            self.optionZigzag2Radio.setEnabled(True)

            self.fps60Radio.setStyleSheet(staticValues.enabledStyleSheet)
            self.fps60Radio.setChecked(False)
            self.fps60Radio.setEnabled(True)

            self.fps120Radio.setStyleSheet(staticValues.enabledStyleSheet)
            self.fps120Radio.setChecked(False)
            self.fps120Radio.setEnabled(True)

            self.OptionsLabel.setStyleSheet(staticValues.enabledStyleSheet)

            self.exceptOptionCheckBox.setStyleSheet(staticValues.enabledStyleSheet)
            self.exceptOptionCheckBox.setChecked(False)
            self.exceptOptionCheckBox.setEnabled(True)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()