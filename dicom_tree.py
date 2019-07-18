'''
View DICOM files in a collapsible tree
Using Qt and PySide
https://github.com/pydicom/contrib-pydicom/blob/master/plotting-visualization/dcm_qt_tree.py
'''

import pydicom
import sys
from PySide2 import QtGui
from PySide2.QtWidgets import QApplication, QTreeView
import collections


class DicomTree(object):
    def __init__(self, filename):
        self.filename = filename

    def show_tree(self):
        ds = self.dicom_to_dataset(self.filename)
        dic = self.dataset_to_dic(ds)
        model = self.dic_to_model(dic)
        self.display(model)

    def array_to_model(self, array):
        # QStandardItemModel provides a generic model for storing custom data
        # https://doc.qt.io/qtforpython/PySide2/QtGui/QStandardItemModel.html
        model = QtGui.QStandardItemModel()

        # Set parentItem to a virtual ROOT item
        parentItem = model.invisibleRootItem()

        for ntuple in array:
            tag = ntuple[0]
            value = ntuple[1]
            # The isinstance() function checks if the object (first argument)
            # is an instance or subclass of classinfo class (second argument).
            if isinstance(value, dict):
                self.recurse_dic_to_item(value, parentItem)
            else:
                item = QtGui.QStandardItem(tag + str(value))
                parentItem.appendRow(item)

        return parentItem

    def dic_to_model(self, dic):
        # Create a custom data model
        model = QtGui.QStandardItemModel()

        # Set parentItem to a virtual ROOT item
        parentItem = model.invisibleRootItem()

        self.recurse_dic_to_item(dic, parentItem)

        return model

    def dataset_to_array(self, dataset):
        # Declare a empty array
        array = []

        # Append every data_element to the array
        for data_element in dataset:
            array.append(self.data_element_to_dic(data_element))

        return array

    def recurse_dic_to_item(self, dic, parent):
        for k in dic:
            v = dic[k]
            # if sub item is a dict then repeat loop
            if isinstance(v, dict):
                item = QtGui.QStandardItem(k + ':' + str(v))
                parent.appendRow(self.recurse_dic_to_item(v, item))
            else:
                item = QtGui.QStandardItem(k + ':' + str(v))
                parent.appendRow(item)

        return parent

    def dicom_to_dataset(self, filename):
        dataset = pydicom.read_file(filename, force=True)

        return dataset

    def data_element_to_dic(self, data_element):
        dic = collections.OrderedDict()
        if data_element.VR == "SQ":
            items = collections.OrderedDict()
            dic[data_element.name] = items
            i = 0
            for dataset_item in data_element:
                items['item ' + str(i)] = self.dataset_to_dic(dataset_item)
                i += 1
        elif data_element.name != 'Pixel Data':
            dic[data_element.name] = data_element.value

        return dic

    def dataset_to_dic(self, dataset):
        dic = collections.OrderedDict()
        for data_element in dataset:
            dic.update(self.data_element_to_dic(data_element))

        return dic

    def display(self, model):
        app = QApplication.instance()

        # Create QApplication if it does not exist
        if not app:
            app = QApplication(sys.argv)

        tree = QTreeView()
        tree.setModel(model)
        tree.show()
        app.exec_()
        return tree


def main():
    filename = './dicom_sample/ct.0.dcm'
    dicomTree = DicomTree(filename)
    dicomTree.show_tree()


if __name__ == '__main__':
    main()