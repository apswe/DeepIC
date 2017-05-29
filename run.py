from utils.loader import construct_input_data
from keras.datasets import cifar10
from keras.utils.np_utils import to_categorical
from utils.preprocessor import shuffle, extractSIFT, resizeImages
from keras.preprocessing.image import ImageDataGenerator
from models.ResSppNet import EnhancedResSppNet
import numpy as np

validation_split = 0.9

class_num = 12
enhanced_class_num = 10

x, y = construct_input_data('./data/train')
x_extra, y_extra = construct_input_data('./data/extra')

x, y = np.concatenate((x, x_extra)), np.concatenate((y, y_extra))

x, y = shuffle(x, y)
x_train, y_train = x[:int(x.shape[0] * validation_split)], y[:int(x.shape[0] * validation_split)]
x_test, y_test = x[int(x.shape[0] * validation_split):], y[int(x.shape[0] * validation_split):]
x_train_sift = extractSIFT(x_train)

(x_train_p, y_train_p), (x_test_p, y_test_p) = cifar10.load_data()
x_train_p, x_test_p = resizeImages(x_train_p, size = (64, 64)), resizeImages(x_test_p, size = (64, 64))
y_train_p = to_categorical(y_train_p, 10)
y_test_p = to_categorical(y_test_p, 10)

x_train_p = x_train_p.astype('float32')
x_test_p = x_test_p.astype('float32')
x_train_p /= 255.
x_test_p /= 255.

print "finish loading data"

classifier, classifier_p, classifier_e = EnhancedResSppNet(class_num = 12, enhanced_class_num = 10)

generator = ImageDataGenerator(
    featurewise_center = False,  # set input mean to 0 over the dataset
    samplewise_center = False,  # set each sample mean to 0
    featurewise_std_normalization = False,  # divide inputs by std of the dataset
    samplewise_std_normalization = False,  # divide each input by its std
    zca_whitening = False,  # apply ZCA whitening
    rotation_range = 0,  # randomly rotate images in the range (degrees, 0 to 180)
    width_shift_range = 0.1,  # randomly shift images horizontally (fraction of total width)
    height_shift_range = 0.1,  # randomly shift images vertically (fraction of total height)
    horizontal_flip = True,  # randomly flip images
    vertical_flip = False  # randomly flip images
)

generator.fit(x_train_p)

classifier_p.fit_generator(generator.flow(x_train_p, y_train_p, batch_size = 32),
                           epochs = 100,
                           verbose = 1,
                           steps_per_epoch = x_train_p.shape[0] // 32,
                           validation_steps = 10,
                           validation_data = (x_test_p, y_test_p))

generator.fit(x_train)

classifier.fit_generator(generator.flow(x_train, y_train, batch_size = 32),
                         epochs = 100,
                         verbose = 1,
                         steps_per_epoch = x_train.shape[0] // 32,
                         validation_steps = 10,
                         validation_data = (x_test, y_test))

classifier_e.fit([x_train, x_train_sift], y_train, batch_size = 32, epochs = 100, validation_split = 0.1, verbose = True)

classifier_e.save_weights('./weights/ResSppNet.h5')
