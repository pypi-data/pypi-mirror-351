"""
Compare two video, found the async part


"""

import pickle
import time
import cv2
import os
import matplotlib.pyplot as plt

import numpy as np

# from dtaidistance import dtw
from scipy.spatial.distance import mahalanobis


def test():
    video1_path = "data/sync_videos/01.mp4"
    video2_path = "data/sync_videos/02.mp4"

    def extract_features(video_path):
        cap = cv2.VideoCapture(video_path)
        features = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # 这里我们使用颜色直方图作为特征
            hist = cv2.calcHist(
                [frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
            )
            hist = cv2.normalize(hist, hist).flatten()
            h = np.mean(hist).astype(np.float32)
            features.append(h)
        cap.release()
        return np.array(features)

    features1 = extract_features(video1_path)
    features2 = extract_features(video2_path)

    print(f"features1: {len(features1)} {features1[0]}")
    print(f"features2: {len(features2)} {features2[0]}")

    # 定义距离度量
    # manhattan_distance = lambda x, y: np.abs(x - y).sum()

    # # 计算 DTW
    # d = dtw(
    #     # features1, features2, dist=manhattan_distance
    #     features1,
    #     features2,
    #     dist_method="euclidean",
    # )
    # dist = d.distance
    # cost_matrix = d.costMatrix
    # path = d.directionMatrix

    # optimal_path = np.array(path).T

    paths = dtw.warping_paths(features1, features2)
    print(paths)

    from dtaidistance import dtw_visualisation as dtwvis

    dtwvis.plot_warping(features1, features2, paths, filename="warp2.png")

    # 提取最优路径
    optimal_path = np.array(paths).T
    # 计算时间错位差
    time_differences = optimal_path[:, 0] - optimal_path[:, 1]

    print(time_differences)


def test2():
    from dtaidistance import dtw
    from dtaidistance import dtw_visualisation as dtwvis
    import numpy as np

    s1 = np.array([0.0, 0, 1, 2, 1, 0, 1, 0, 0, 2, 1, 0, 0])
    s2 = np.array([0.0, 1, 2, 3, 1, 0, 0, 0, 2, 1, 0, 0, 0, 3, 4, 0, 3, 4])
    path = dtw.warping_path(s1, s2)
    dtwvis.plot_warping(s1, s2, path, filename="warp.png")


def get_features(frame, method="sift"):
    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    h = np.mean(hist).astype(np.float32)
    return h


def test3():

    def extract_features(video_path, sample_fps=2):
        cap = cv2.VideoCapture(video_path)
        features = []

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        if original_fps == 0:
            raise ValueError("Failed to get FPS from video")

        frame_interval = int(original_fps / sample_fps)

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only process frames at the specified sample rate
            if frame_count % frame_interval == 0:
                # Use color histogram as feature
                h = get_features(frame)
                features.append(h)

            frame_count += 1

        cap.release()
        return np.array(features)

    features1 = extract_features(video1_path)
    features2 = extract_features(video2_path)

    print(f"features1: {len(features1)} {features1[0]}")
    print(f"features2: {len(features2)} {features2[0]}")

    # 定义距离度量
    # manhattan_distance = lambda x, y: np.abs(x - y).sum()

    # # 计算 DTW
    # d = dtw(
    #     # features1, features2, dist=manhattan_distance
    #     features1,
    #     features2,
    #     dist_method="euclidean",
    # )
    # dist = d.distance
    # cost_matrix = d.costMatrix
    # path = d.directionMatrix

    # optimal_path = np.array(path).T

    paths = dtw.warping_path(features1, features2)
    print(paths)

    from dtaidistance import dtw_visualisation as dtwvis

    dtwvis.plot_warping(features1, features2, paths, filename="results/warp2.png")

    # 提取最优路径
    optimal_path = np.array(paths).T
    # 计算时间错位差
    time_differences = optimal_path[:, 0] - optimal_path[:, 1]

    print(time_differences)


def test4():
    global feature_extractor
    global matcher
    feature_extractor = cv2.ORB_create()

    FLANN_INDEX_LSH = 6
    index_params = dict(
        algorithm=FLANN_INDEX_LSH,
        table_number=6,  # 12
        key_size=12,  # 20
        multi_probe_level=1,
    )  # 2
    search_params = dict(checks=50)  # or pass an empty dictionary
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    # matcher = cv2.BFMatcher()

    def extract_sift_features(image):
        # sift = cv2.SIFT_create()
        keypoints, descriptors = feature_extractor.detectAndCompute(image, None)
        return keypoints, descriptors

    def euclidean_distance(descriptor1, descriptor2):
        return np.linalg.norm(descriptor1 - descriptor2)

    def match_features(descriptors1, descriptors2):
        matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
        # print(matches)
        good_matches = []
        for match in matches:
            if len(match) == 2:
                m, n = match
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
        return good_matches

    def calculate_similarity(image1, image2):
        keypoints1, descriptors1 = extract_sift_features(image1)
        keypoints2, descriptors2 = extract_sift_features(image2)
        good_matches = match_features(descriptors1, descriptors2)
        similarity = len(good_matches) / min(len(keypoints1), len(keypoints2))
        return similarity

    def run_video(video_path, sample_fps=2):
        cap = cv2.VideoCapture(video_path)
        features = []

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        if original_fps == 0:
            raise ValueError("Failed to get FPS from video")

        frame_interval = int(original_fps / sample_fps)

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only process frames at the specified sample rate
            if frame_count % frame_interval == 0:
                # Use color histogram as feature
                h = get_features(frame)
                features.append(h)

            frame_count += 1

        cap.release()
        return np.array(features)

    def calculate_similarity_matrix(video1, video2, sample_fps=2):
        cap1 = cv2.VideoCapture(video1)
        cap2 = cv2.VideoCapture(video2)

        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        fps2 = cap2.get(cv2.CAP_PROP_FPS)

        frame_interval1 = int(fps1 / sample_fps)
        frame_interval2 = int(fps2 / sample_fps)

        similarities = []

        frame_idx1 = 0
        while True:
            cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_idx1)
            ret1, frame1 = cap1.read()
            if not ret1:
                break
            keypoints1, descriptors1 = extract_sift_features(frame1)

            frame_similarities = []
            frame_idx2 = 0
            while True:
                cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_idx2)
                ret2, frame2 = cap2.read()
                if not ret2:
                    break
                keypoints2, descriptors2 = extract_sift_features(frame2)
                similarity = match_features(descriptors1, descriptors2)
                frame_similarities.append(similarity)

                frame_idx2 += frame_interval2

            similarities.append(frame_similarities)
            frame_idx1 += frame_interval1

        cap1.release()
        cap2.release()

        return np.array(similarities)

    def extract_features(video_path, sample_fps=2, limit_max_frames=100):
        cap = cv2.VideoCapture(video_path)
        features = []

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        if original_fps == 0:
            raise ValueError("Failed to get FPS from video")

        frame_interval = int(original_fps / sample_fps)

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only process frames at the specified sample rate
            if frame_count % frame_interval == 0:
                # Use color histogram as feature
                keypoints2, descriptors2 = extract_sift_features(frame)
                features.append((len(keypoints2), descriptors2))
            if len(features) > limit_max_frames:
                break
            frame_count += 1

        cap.release()
        return features

    def calculate_similarity_matrix2(
        video1,
        video2,
        sample_fps=2,
        rerun_cost_m=False,
    ):
        # 6 min at least
        limit_max_frames = 360 * sample_fps
        cache_f = os.path.join(
            "results", f"{os.path.basename(video1)}__{os.path.basename(video2)}.pkl"
        )
        if os.path.exists(cache_f):
            res = pickle.load(open(cache_f, "rb"))
            if "fea1" in res:
                fea1 = res["fea1"]
                fea2 = res["fea2"]

                if "similarities" in res.keys():
                    return res["similarities"]
        else:
            fea1 = extract_features(
                video1, sample_fps, limit_max_frames=limit_max_frames
            )
            fea2 = extract_features(
                video2, sample_fps, limit_max_frames=limit_max_frames
            )

            with open(cache_f, "wb") as f:
                pickle.dump({"fea1": fea1, "fea2": fea2}, f)
                print("result cached")

        print(f"fea done, {len(fea1)} {len(fea2)} {fea1[0]}")

        similarities = np.full((len(fea1), len(fea2)), 0).astype(np.float64)
        print(similarities.shape)

        t1 = time.time()
        for i, f1 in enumerate(fea1):
            for j, f2 in enumerate(fea2):
                if i == 0 and j == 100:
                    print(f"100 cost: {time.time() - t1}")
                good_matches = match_features(f1[1], f2[1])
                # print(similarity)
                similarity = len(good_matches) / min(f1[0], f2[0])
                # print(similarity)
                similarities[i, j] = similarity
        # print(similarities)

        with open(cache_f, "wb") as f:
            pickle.dump({"fea1": fea1, "fea2": fea2, "similarities": similarities}, f)
            print("result cached")
        return similarities

    # video2_path = "data/align/ci46e75euhfi85cfak2g_0515-初舞台-CAM10-REC17_S001_S001_T002_transcode_114200_9min.mp4"

    simi_matrix = calculate_similarity_matrix2(video1_path, video2_path)
    print(simi_matrix.shape)
    print(simi_matrix)
    aa = np.argmax(simi_matrix, axis=-1)
    print(aa)
    bb = np.argmax(simi_matrix, axis=0)
    print(bb)

    from dtw import dtw

    alignment = dtw(simi_matrix)

    print(alignment)
    print(alignment.distance)
    np.set_printoptions(threshold=np.inf)
    print(alignment.index1)
    print(alignment.index2)
    # alignment.plot(type="twoway",offset=-2)
    # plt.savefig('results/warp3.png')

    # path = dtw.distance_matrix(simi_matrix)

    # print(path)

    # from dtaidistance import dtw_visualisation as dtwvis

    # dtwvis.plot_matrix(path, filename="results/warp2.png")

    # matching_frames = [(path[0][i], path[1][i]) for i in range(len(path[0]))]
    # return matching_frames


test4()
# test2()
