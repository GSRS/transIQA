import matplotlib.pyplot as plt
import cv2
import numpy as np
from torchvision import transforms
from torch.utils.data import DataLoader
import dataset


def read_txt(image_path):

    images = [line.rstrip('\n').split()[0] for line in open(image_path)]
    scores = [line.rstrip('\n').split()[1] for line in open(image_path)]

    return images, scores

def show_image(image, title='default', commit=''):
    plt.title(str(title))
    plt.imshow(image)
    if commit != '':
        print(commit)
    plt.pause(0.01)
    plt.show()

def show_image_depth(image_path):
    image = io.imread(image_path)
    path = ''
    if len(image.shape)!=3:
        path = image_path
        print(path, image.shape)

    return path


def prepare_faces(scale = 1.2):
    import dlib

    image_list = './data/image_score_generated_dlib.txt'
    output_root = '../dataset/transIQA/faces'
    output_file = 'face_score_generated_dlib.txt'

    dlib_model_path = './model/mmod_human_face_detector.dat'

    images = [line.rstrip('\n').split()[0] for line in open(image_list)]
    scores = [line.rstrip('\n').split()[1] for line in open(image_list)]
    face_detector = dlib.cnn_face_detection_model_v1(dlib_model_path)
    faces = []
    face_scores = []

    print('Datasets reading and Face detecting')
    # prepare faces
    # detect faces and save as images file

    # read images and detect faces
    pristine_images = []
    num_pristine = int(len(images) / 21)
    for i in range(num_pristine):
        pristine_images.append(images[i * 21])

    # detect faces for one pristine
    for i in range(len(pristine_images)):
        print('Reading images: %s'%pristine_images[i])
        image_name = osp.splitext(osp.split(pristine_images[i])[1])[0]

        image = cv2.imread(pristine_images[i])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        dets = face_detector(image, 1)

        # get face locations
        face_locations = []
        for _, d in enumerate(dets):
            if d.confidence > 0.5:
                left, right, top, bottom = d.rect.left(), d.rect.right(), d.rect.top(), d.rect.bottom()
                height = bottom - top
                width = right - left
                central = (int((top+bottom)*0.5), int((left+right)*0.5))

                #scale image
                top = max(int(central[0] - height * scale * 0.5), 0)
                bottom = min(int(central[0] + height * scale * 0.5), image.shape[0])
                left = max(int(central[1] - width * scale * 0.5), 0)
                right = min(int(central[1] + width * scale * 0.5), image.shape[1])

                face_locations.append([top, bottom, left, right])

        # crop exist datasets
        if len(face_locations) > 0:
            for j in range(4*5+1):
                image = cv2.imread(images[i*21 + j])
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                score = scores[i*21 + j]
                face_num = 0
                for location in face_locations:
                    #suffix

                    face_num += 1
                    suffix = osp.split(osp.split(images[i*21 + j])[0])[1] + '_' + str(face_num)

                    image_path = output_root + '/' + image_name + '_' + suffix + '.npy'
                    #print('saving numpy image: %s'%image_path)
                    np.save(image_path, image[location[0]:location[1], location[2]:location[3], :])

                    faces.append(image_path)
                    face_scores.append(score)

                    #debug
                    debug=0
                    if debug:
                        plt.imshow(np.load(image_path))
                        plt.title(str(score))
                        plt.show()

        print('%d in %d'%(i, len(pristine_images)))



    with open('../dataset/transIQA' + '/' + output_file, 'w') as f:
        for i in range(len(faces)):
            f.write(faces[i] + ' ' +str(face_scores[i]) + '\n')


def get_dataset(train=True,
                image_list='',
                transform=transforms.Compose([
                    dataset.RandomCrop(32),
                    dataset.ToTensor()
                ]),
                num_faces=10000):

    if train:
        face_dataset = dataset.FaceScoreDataset(image_list=image_list,
                                                transform = transform,
                                                num_faces = num_faces)

    else:
        face_dataset = dataset.FaceScoreDataset(train=False,
                                                image_list=image_list)

    return face_dataset

def get_dataloader(face_dataset, batch_size, shuffle=True, num_workers=4):

    return DataLoader(face_dataset, batch_size=batch_size,
                     shuffle=shuffle, num_workers=num_workers)

def get_dataset_small(train=True,
                image_list='',
                transform=transforms.Compose([
                    dataset.RandomCrop(32),
                    dataset.ToTensor()
                ]),
                num_faces=10000):

    if train:
        face_dataset = dataset.FaceScoreDataset_small(image_list=image_list,
                                                transform = transform,
                                                num_faces = num_faces)

    else:
        face_dataset = dataset.FaceScoreDataset_small(train=False,
                                                image_list=image_list)

    return face_dataset


def np_load(path):
    print(path)
    return np.load(path)