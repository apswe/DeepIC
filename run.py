import cv2
import numpy as np
from keras.preprocessing.image import ImageDataGenerator

from models.ResSppNet import ResnetBuilder
from utils.loader import construct_input_data
from utils.preprocessor import shuffle, extractSIFT
from keras.optimizers import RMSprop

validation_split = 0.9

class_num = 12
enhanced_class_num = 10

x, y = construct_input_data('./data/train', with_masks = True)
x_extra, y_extra = construct_input_data('./data/extra', with_masks = True)

x, y = x + x_extra, np.concatenate((y, y_extra))

# x_sift = extractSIFT(x, n_clusters = 100)

x = np.asarray([np.reshape(cv2.resize(item, (128, 128)), newshape = (128, 128, 3)) for item in x])

x, y = x.astype(np.float32), y.astype(np.float32)

x /= 255.

x, y, x_sift = shuffle(x, y, None)

# x, y, x_sift = shuffle(x, y, x_sift)

# x_train, x_train_sift, y_train = x[:int(x.shape[0] * validation_split)], x_sift[:int(x.shape[0] * validation_split)], y[
#                                                                                                                       :int(
#                                                                                                                           x.shape[
#                                                                                                                               0] * validation_split)]
# x_test, x_test_sift, y_test = x[int(x.shape[0] * validation_split):], x_sift[int(x.shape[0] * validation_split):], y[
#                                                                                                                    int(
#                                                                                                                        x.shape[
#                                                                                                                            0] * validation_split):]


class_weight = 1. - np.asarray([0.9231, 0.5526, 0.9333, 0.5357, 0.375, 0.871, 0.7692, 0.68, 0.7407, 0.6, 0.5862, 0.3636])

x_train, y_train = x[:int(x.shape[0] * validation_split)], y[:int(x.shape[0] * validation_split)]
x_test, y_test = x[int(x.shape[0] * validation_split):], y[int(x.shape[0] * validation_split):]

# (x_train_p, y_train_p), (x_test_p, y_test_p) = cifar10.load_data()
# x_train_p, x_test_p = resizeImages(x_train_p, size = (128, 128)), resizeImages(x_test_p, size = (128, 128))
# y_train_p = to_categorical(y_train_p, 10)
# y_test_p = to_categorical(y_test_p, 10)
# #
# x_train_p = x_train_p.astype('float32')
# x_test_p = x_test_p.astype('float32')
# x_train_p /= 255.
# x_test_p /= 255.

print "finish loading data"

# classifier, classifier_p = EnhancedResSppNet(class_num = 12, enhanced_class_num = 10)

# classifier, classifier_p, classifier_e = EnhancedResSppNet(class_num = 12, enhanced_class_num = 10)

classifier = ResnetBuilder.build_resnet_34(input_shape = (3, 128, 128), num_outputs = 12, enhanced = False)

# classifier, classifier_p = ResnetBuilder.build_resnet_34(input_shape = (3, 128, 128), num_outputs = 12, enhanced = False)
# classifier_p.compile(loss = "categorical_crossentropy", optimizer = RMSprop(lr = 1e-3, decay = 1e-3),
#                      metrics = ['accuracy'])
classifier.compile(loss = "categorical_crossentropy", optimizer = RMSprop(lr = 5e-4, decay = 1e-3),
                   metrics = ['accuracy'])

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

# generator.fit(x_train_p)
#
# classifier_p.fit_generator(generator.flow(x_train_p, y_train_p, batch_size = 128),
#                            epochs = 100,
#                            verbose = 1,
#                            steps_per_epoch = x_train_p.shape[0] // 128,
#                            validation_steps = 1,
#                            validation_data = (x_test_p, y_test_p))

generator.fit(x_train)

classifier.fit_generator(generator.flow(x_train, y_train, batch_size = 32),
                         epochs = 500,
                         verbose = 1,
                         steps_per_epoch = x_train.shape[0] // 32,
                         validation_steps = 10,
                         validation_data = (x_test, y_test),
                         class_weight = class_weight)

classifier.save_weights('./weights/ResSppNet.h5')

# classifier_p.fit(x_train_p, y_train_p, batch_size = 128, validation_split = 0.1, epochs = 100, shuffle = True, verbose = True)

# classifier_p.fit(x_train_p, y_train_p, batch_size = 128, validation_data = (x_test_p, y_test_p), epochs = 100, shuffle = True, verbose = True)

# classifier.fit(x, y, batch_size = 32, validation_split = 0.1, epochs = 200, shuffle = True, verbose = True)

# classifier.fit(x_train, y_train, batch_size = 32, validation_data = (x_test, y_test), epochs = 200, shuffle = True, verbose = True)

# classifier.fit(x = [x_train, x_train_sift], y = y_train, batch_size = 32,
#                validation_data = [[x_test, x_test_sift], y_test], epochs = 200, shuffle = True, verbose = True)

# table = group_data_by_label(x_test, y_test)
#
# for key in table:
#     print "accuracy for class: %d is %.4f" % (key, classifier.evaluate(table[key]["images"], table[key]["labels"])[1])


# KFold = StratifiedKFold(n_splits = 10)

# print cross_val_score(classifier, x, y, cv = KFold)

# classifier_e.fit([x_train, x_train_sift], y_train, batch_size = 32, epochs = 100, validation_split = 0.1, verbose = True)

# classifier_e.save_weights('./weights/ResSppNet.h5')
