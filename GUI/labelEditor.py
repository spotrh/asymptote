from pyUIClass.labelTextEditor import Ui_Dialog
import PyQt5.QtWidgets as Qw
import PyQt5.QtSvg as Qs
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc
import xasyArgs as xa
import xasy2asy as x2a
import xasyOptions as xo
import xasyUtils as xu
import tempfile
import uuid
import os


class labelEditor(Qw.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.btnAccept.clicked.connect(self.accept)
        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.chkMathMode.stateChanged.connect(self.chkMathModeChecked)
        self.ui.btnPreview.clicked.connect(self.btnPreviewOnClick)
        self.ui.btnGetText.clicked.connect(self.btnGetTextOnClick)

        self.svgPreview = None

    def chkMathModeChecked(self, checked):
        self.ui.cmbMathStyle.setEnabled(checked)

    def getText(self):
        rawText = self.ui.txtLabelEdit.toPlainText()
        rawText.replace('\n', ' ')
        if self.ui.chkMathMode.isChecked():
            prefix = ''
            if self.ui.cmbMathStyle.currentText() == 'Display Style':
                prefix = '\\displaystyle'
            elif self.ui.cmbMathStyle.currentText() == 'Script Style':
                prefix = '\\scriptstyle'
            return '${0}{{{1}}}$'.format(prefix, rawText)
        else:
            return rawText

    def btnPreviewOnClick(self):
        path = xa.getArgs().asypath
        if path is None:
            opt = xo.xasyOptions().load()
            path = opt['asyPath']

        asyInput = """
        file fout=output(mode='pipe');
        frame f;
        label(f, "{0}");
        write(fout, min(f), newl);
        write(fout, max(f), newl);
        shipout(f);
        flush(fout);
        """

        with tempfile.TemporaryDirectory(prefix='xasylbl_') as tmpdir:
            tmpFile = os.path.join(tmpdir, 'lbl-{0}.svg'.format(str(uuid.uuid4())))
            with x2a.AsymptoteEngine(path, customOutdir=tmpFile, args=['-f svg']) as asy:
                asy.ostream.write(asyInput.format(self.getText()))
                asy.ostream.flush()

                bounds_1 = asy.istream.readline().strip()
                bounds_2 = asy.istream.readline().strip()

            min_bounds = xu.listize(bounds_1, (float, float))
            max_bounds = xu.listize(bounds_2, (float, float))

            new_rect = self.processBounds(min_bounds, max_bounds)

            self.svgPreview = Qs.QSvgRenderer()
            self.svgPreview.load(tmpFile)

            self.drawPreview(new_rect)
            # self.ui.lblLabelPreview.setSizePolicy(Qw.QSizePolicy.Ignored, Qw.QSizePolicy.Ignored)

    def drawPreview(self, naturalBounds):
        img = Qg.QPixmap(self.ui.lblLabelPreview.size())
        img.fill(Qg.QColor.fromRgbF(1, 1, 1, 1))
        if self.svgPreview is None:
            pass
        else:
            with Qg.QPainter(img) as pnt:
                scale_ratio = self.getIdealScaleRatio(naturalBounds, self.ui.lblLabelPreview.rect())

                pnt.translate(self.ui.lblLabelPreview.rect().center())
                pnt.scale(scale_ratio, scale_ratio)
                self.svgPreview.render(pnt, naturalBounds)
            self.ui.lblLabelPreview.setPixmap(img)


    def getIdealScaleRatio(self, rect, boundsRect):
        assert isinstance(rect, (Qc.QRect, Qc.QRectF))
        assert isinstance(rect, (Qc.QRect, Qc.QRectF))

        magic_ratio = 0.50
        idealRatioHeight = (magic_ratio * boundsRect.height()) / rect.height()
        magicRatioWidth = 0.50

        if idealRatioHeight * rect.width() > magicRatioWidth * boundsRect.width():
            idealRatioWidth = (magicRatioWidth * boundsRect.width()) / rect.width()
            idealRatio = min(idealRatioHeight, idealRatioWidth)
        else:
            idealRatio = idealRatioHeight
        return idealRatio

    def processBounds(self, minPt, maxPt):
        p1x, p1y = minPt
        p2x, p2y = maxPt

        minPt = Qc.QPointF(p1x, p1y)
        maxPt = Qc.QPointF(p2x, p2y)

        newRect = Qc.QRectF(minPt, maxPt)
        return newRect


    def btnGetTextOnClick(self):
        msgbox = Qw.QMessageBox()
        msgbox.setText('Text Preview:\n' + self.getText())
        msgbox.setWindowTitle('Text preview')
        msgbox.show()
        return msgbox.exec_()