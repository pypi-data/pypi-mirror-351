import tartanair as ta
tartanair_data_root = '/data/tartanair_v2'
ta.init(tartanair_data_root)

# # ta.download(env = "AncientTowns", 
# #             difficulty = ['easy'], #, 'hard'
# #             modality = ['flow', 'seg'], 
# #             camera_name = ['lcam_left','lcam_right','lcam_equirect','lcam_fish'])
# ta.download(env = ["Gascola"], 
#             difficulty = ['hard',], #, 'hard'
#             modality = ['image'], 
#             camera_name = ['rcam_front'],
#             unzip = False)


# import tartanair as ta
# ta.init('/data/tartanair_v2')
# from scipy.spatial.transform import Rotation
# R_raw_new0 = Rotation.from_euler('y', 45, degrees=True).as_matrix().tolist()

# cam_model_0 =  {'name': 'pinhole',
#                 'raw_side': 'left', # TartanAir has two cameras, one on the left and one on the right. This parameter specifies which camera to use.
#                 'params':
#                         {'fx': 320,
#                          'fy': 320,
#                          'cx': 320,
#                          'cy': 320,
#                          'width': 640,
#                          'height': 640},
#                 'R_raw_new': R_raw_new0}

# R_raw_new1 = Rotation.from_euler('xyz', [45, 0, 0], degrees=True).as_matrix().tolist()

# cam_model_1 = {'name': 'doublesphere',
#                 'raw_side': 'left',
#                 'params':
#                         {'fx': 300,
#                         'fy': 300,
#                         'cx': 500,
#                         'cy': 500,
#                         'width': 1000,
#                         'height': 1000,
#                         'alpha': 0.6,
#                         'xi': -0.2,
#                         'fov_degree': 195},
#                 'R_raw_new': R_raw_new1}
# ta.customize(env = 'coalmine',
#              difficulty = 'easy',
#              trajectory_id = ['P004'],
#              modality = ['depth', 'seg', 'image'],
#              new_camera_models_params=[cam_model_0, cam_model_1],
#              num_workers = 6
#              )

# import cv2
# import numpy as np
# img1=cv2.imread('/data/tartanair_v2/coalmine/Data_easy/P004/image_lcam_custom0_pinhole/000331_lcam_image_custom0_pinhole.png')
# img2=cv2.imread('/data/tartanair_v2/coalmine/Data_easy/P004/image_lcam_custom0_pinhole_torch/000331_lcam_image_custom0_pinhole.png')
# diff = np.abs(img1.astype(np.float32)-img2.astype(np.float32)).astype(np.uint8)
# import ipdb;ipdb.set_trace()

# import numpy as np
# import cv2
# from tartanair.data_cacher.utils import visdepth
# np.set_printoptions(precision=2)

# # Specify the environments, difficulties, and trajectory ids to load.
# envs = ['CoalMine']
# difficulties = ['hard']
# trajectory_ids = [] 

# # Specify the modalities to load.
# modalities = ['image', 'depth', 'pose', 'imu']
# camnames = ['lcam_front', 'lcam_left']

# # Specify the dataloader parameters.
# new_image_shape_hw = [640, 640] # If None, no resizing is performed. If a value is passed, then the image is resized to this shape.
# subset_framenum = 100 # This is the number of frames in a subset. Notice that this is an upper bound on the batch size. Ideally, make this number large to utilize your RAM efficiently. Information about the allocated memory will be provided in the console.
# seq_length = {'image': 2, 'depth': 1, 'imu': 20} # This is the length of the data-sequences. For example, if the sequence length is 2, then the dataloader will load pairs of images.
# seq_stride = 1 # This is the stride between the data-sequences. For example, if the sequence length is 2 and the stride is 1, then the dataloader will load pairs of images [0,1], [1,2], [2,3], etc. If the stride is 2, then the dataloader will load pairs of images [0,1], [2,3], [4,5], etc.
# frame_skip = 0 # This is the number of frames to skip between each frame. For example, if the frame skip is 2 and the sequence length is 3, then the dataloader will load frames [0, 3, 6], [1, 4, 7], [2, 5, 8], etc.
# batch_size = 8 # This is the number of data-sequences in a mini-batch.
# num_workers = 4 # This is the number of workers to use for loading the data.
# shuffle = False # Whether to shuffle the data. Let's set this to False for now, so that we can see the data loading in a nice video. Yes it is nice don't argue with me please. Just look at it! So nice. :)

# # Create a dataloader object.
# dataloader = ta.dataloader(env = envs,
#             difficulty = difficulties,
#             trajectory_id = trajectory_ids,
#             modality = modalities,
#             camera_name = camnames,
#             new_image_shape_hw = new_image_shape_hw,
#             seq_length = seq_length,
#             subset_framenum = subset_framenum,
#             seq_stride = seq_stride,
#             frame_skip = frame_skip,
#             batch_size = batch_size,
#             num_workers = num_workers,
#             shuffle = shuffle,
#             verbose = True)

# # Iterate over the batches.
# for i in range(100):
#     # Get the next batch.
#     batch = dataloader.load_sample()
#     # Check if the batch is None.
#     if batch is None:
#         break
#     print("Batch number: {}".format(i), "Loaded {} samples so far.".format(i * batch_size))

#     for b in range(batch_size):
#         # Visualize some images.
#         # The shape of an image batch is (B, S, H, W, C), where B is the batch size, S is the sequence length, H is the height, W is the width, and C is the number of channels.
#         img0 = batch['image_lcam_front'][b][0].numpy().transpose(1,2,0)
#         img1 = batch['image_lcam_left'][b][1].numpy().transpose(1,2,0)
#         depth0 = batch['depth_lcam_front'][b][0].numpy()
#         depth1 = batch['depth_lcam_left'][b][0].numpy()
#         pose = batch['pose_lcam_front'].numpy()
#         imu = batch['imu'].numpy()

#         # Visualize the images.
#         depth0 = visdepth(80./depth0)
#         depth1 = visdepth(80./depth1)
#         outimg = np.concatenate((img0, img1), axis = 1)
#         outdepth = np.concatenate((depth0, depth1), axis = 1)
#         disp = np.concatenate((outimg, outdepth), axis = 0)
#         disp = cv2.resize(disp, (0,0), fx=0.5, fy=0.5)
#         cv2.imshow('outimg', disp)
#         cv2.waitKey(10)

#         print("  Pose: ", pose[b][0])
#         print("  IMU: ", imu[b][0])

# dataloader.stop_cachers()