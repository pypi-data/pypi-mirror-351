"""

We need clustering speakers with embeddings

"""

from collections import Counter
from typing import Tuple
import numpy as np
import umap.umap_ as umap

from sklearn.cluster._kmeans import k_means
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

from loguru import logger
from scipy.spatial.distance import cosine
import hdbscan


"""

The method from funasr is extremly bad..

"""


import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def merge_similar_labels_once(
    labels, embeddings, min_count=3, similarity_threshold=0.5, debug=False
):
    unique_labels = np.unique(labels)
    label_mean_embs = {}
    label_counts = {}

    for label in unique_labels:
        mask = np.array(labels) == label
        label_mean_embs[label] = np.mean(np.array(embeddings)[mask], axis=0)
        label_counts[label] = np.sum(mask)

    # 计算平均embedding之间的相似度矩阵
    mean_embeddings = np.array([label_mean_embs[label] for label in unique_labels])
    similarity_matrix = cosine_similarity(mean_embeddings)

    # 打印混淆矩阵
    if debug:
        df = pd.DataFrame(similarity_matrix, index=unique_labels, columns=unique_labels)
        print("\nConfusion Matrix:")
        print(df)

    # 合并低频标签
    label_mapping = {}
    low_freq_labels = {
        label for label, count in label_counts.items() if count < min_count
    }

    for low_freq_label in low_freq_labels:
        idx = list(unique_labels).index(low_freq_label)
        max_sim = -1
        merged_label = low_freq_label

        for i, other_label in enumerate(unique_labels):
            if other_label != low_freq_label and other_label not in low_freq_labels:
                sim = similarity_matrix[idx][i]
                if sim > similarity_threshold and sim > max_sim:
                    max_sim = sim
                    merged_label = other_label

        label_mapping[low_freq_label] = merged_label
        if low_freq_label != merged_label and debug:
            print(
                f"Merged {low_freq_label}({label_counts[low_freq_label]}) into {merged_label}({label_counts[merged_label]}) (similarity: {max_sim:.3f})"
            )

    new_labels = [label_mapping.get(label, label) for label in labels]
    return new_labels


class UmapHdbscan:
    r"""
    Reference:
    - Siqi Zheng, Hongbin Suo. Reformulating Speaker Diarization as Community Detection With
      Emphasis On Topological Structure. ICASSP2022
    """

    def __init__(
        self,
        n_neighbors=20,
        n_components=60,
        min_samples=10,
        min_cluster_size=10,
        metric="cosine",
    ):
        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.min_samples = min_samples
        self.min_cluster_size = min_cluster_size
        self.metric = metric

    def __call__(self, X, merge_thresh=0, batch_segments=100):

        umap_X = umap.UMAP(
            n_neighbors=self.n_neighbors,
            min_dist=0.0,
            n_components=min(self.n_components, X.shape[0] - 2),
            metric=self.metric,
        ).fit_transform(X)
        labels = hdbscan.HDBSCAN(
            min_samples=self.min_samples,
            min_cluster_size=self.min_cluster_size,
            allow_single_cluster=True,
        ).fit_predict(umap_X)
        return labels


class SimpleClustering:
    def __init__(self, sim_threshold=0.4) -> None:
        self.sim_threshold = sim_threshold

    def __call__(
        self,
        embeddings: np.ndarray,
        merge_thresh=0,
        batch_segments=100,
        debug=False,
        merge_until_cos_thresh=0.8,
    ) -> np.ndarray:
        """
        We have to using a batch segments to do it?
        """
        # print(embeddings.shape)
        total_segments = embeddings.shape[0]
        num_batches = (total_segments + batch_segments - 1) // batch_segments

        all_labels = []
        all_centroids = []
        # overlap = min(10, batch_segments // 2)
        overlap = min(40, batch_segments // 2)

        global_label_counter = 0

        for i in range(num_batches):
            start = max(0, i * batch_segments - overlap)
            end = min(total_segments, (i + 1) * batch_segments + overlap)

            batch_embeddings = embeddings[start:end, :]
            batch_labels, batch_centroids = self.batch_clustering(
                batch_embeddings,
                merge_thresh,
                debug=debug,
                merge_until_cos_thresh=merge_until_cos_thresh,
            )

            if i > 0:
                prev_end = min(i * batch_segments + overlap, total_segments)
                overlap_region = slice(prev_end - start - overlap, prev_end - start)
                (
                    batch_labels,
                    batch_centroids,
                    global_label_counter,
                ) = self._stitch_batches(
                    all_labels[-1],
                    all_centroids[-1],
                    batch_labels,
                    batch_centroids,
                    overlap_region,
                    global_label_counter,
                    debug,
                )
            else:
                # For the first batch, update labels to start from 0
                unique_labels = np.unique(batch_labels)
                label_map = {label: i for i, label in enumerate(unique_labels)}
                batch_labels = np.array([label_map[label] for label in batch_labels])
                batch_centroids = {label_map[k]: v for k, v in batch_centroids.items()}
                global_label_counter = len(unique_labels)

            if i < num_batches - 1:
                batch_labels = batch_labels[:-overlap]
                batch_centroids = {
                    k: v for k, v in batch_centroids.items() if k in batch_labels
                }
            if debug:
                logger.info(f"crt batch: {i}, labels: {batch_labels}")
            all_labels.append(batch_labels)
            all_centroids.append(batch_centroids)

        final_labels = np.concatenate(all_labels)
        return final_labels

    def batch_clustering(
        self,
        embeddings: np.ndarray,
        merge_thresh=0,
        merge_until_cos_thresh=0.8,
        debug=False,
    ) -> np.ndarray:
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - self.sim_threshold,
            metric="cosine",
            linkage="average",
        )
        labels = clustering.fit_predict(embeddings)

        if debug:
            logger.info(f"labels before merge: {labels}")

        # another merging step, merge until there is no similar cluster
        labels = self.merge_by_cos(
            labels=labels, embs=embeddings, cos_thr=merge_until_cos_thresh
        )
        if debug:
            logger.info(f"labels after cos merge infinite loop: {labels}")

        counter = Counter(labels)
        small_clusters = {label for label, count in counter.items() if count < 3}

        if small_clusters and merge_thresh > 0:
            if debug:
                logger.info(
                    f"found small clusters: {small_clusters}, these sentence less than 3."
                )
            cluster_centers = np.array(
                [embeddings[labels == i].mean(axis=0) for i in range(max(labels) + 1)]
            )
            new_labels = labels.copy()
            for i, label in enumerate(labels):
                if label in small_clusters:
                    similarities = cosine_similarity([embeddings[i]], cluster_centers)[
                        0
                    ]
                    valid_clusters = [
                        j for j in range(len(similarities)) if j not in small_clusters
                    ]
                    best_match = max(valid_clusters, key=lambda x: similarities[x])

                    if similarities[best_match] > merge_thresh:
                        new_labels[i] = best_match
                        if debug:
                            logger.info(
                                f"replace small cluster {label} to {best_match}, score: {similarities[best_match]}"
                            )
                    else:
                        if debug:
                            logger.info(
                                f"pass replace small cluster {label} to {best_match}, as score: {similarities[best_match]} too low."
                            )
            labels = new_labels
            unique_labels = np.unique(labels)
            centroids = {
                label: embeddings[labels == label].mean(axis=0)
                for label in unique_labels
            }
        if debug:
            logger.info(f"labels normal merge 2: {labels}")

        # labels = self.merge_by_cos(
        #     labels=labels, embs=embeddings, cos_thr=0.6
        # )
        # unique_labels = np.unique(labels)
        # centroids = {
        #     label: embeddings[labels == label].mean(axis=0) for label in unique_labels
        # }
        # if debug:
        #     logger.info(f"labels after final cos merge infinite loop: {labels}")
        new_labels = merge_similar_labels_once(
            labels, embeddings, min_count=3, similarity_threshold=0.5, debug=debug
        )
        unique_labels = np.unique(new_labels)
        centroids = {
            label: embeddings[labels == label].mean(axis=0) for label in unique_labels
        }
        return new_labels, centroids

    def _stitch_batches(
        self,
        prev_labels: np.ndarray,
        prev_centroids: dict,
        curr_labels: np.ndarray,
        curr_centroids: dict,
        overlap_region: slice,
        global_label_counter: int,
        debug=False,
    ) -> Tuple[np.ndarray, dict, int]:
        overlap_prev = prev_labels[-len(curr_labels[overlap_region]) :]
        overlap_curr = curr_labels[overlap_region].tolist()
        logger.info(f"previous labels: {overlap_prev}, current_labels: {overlap_curr}")

        label_map = {}
        for curr_label in np.unique(overlap_curr):
            curr_centroid = curr_centroids[curr_label]
            best_match = None
            best_similarity = -np.inf

            for prev_label in np.unique(overlap_prev):
                prev_centroid = prev_centroids[prev_label]
                similarity = 1 - cosine(curr_centroid, prev_centroid)

                if similarity > best_similarity and similarity > self.sim_threshold:
                    best_similarity = similarity
                    best_match = prev_label

            if best_match is not None:
                label_map[curr_label] = best_match
            else:
                label_map[curr_label] = global_label_counter
                global_label_counter += 1
        new_labels = np.array([label_map.get(label, label) for label in curr_labels])
        new_centroids = {label_map.get(k, k): v for k, v in curr_centroids.items()}
        if debug:
            logger.info(
                f"stitching: labelmap: {label_map}, curr_labels: {curr_labels}, new_labels: {new_labels}"
            )
        return new_labels, new_centroids, global_label_counter

    def merge_clusters(
        self,
        labels,
        embeddings,
        small_cluster_count_thresh=3,
        merge_thresh=0.35,
        cos_thresh=0.8,
    ):
        def get_centroids(labels, embeddings):
            unique_labels = np.unique(labels)
            return {
                label: embeddings[labels == label].mean(axis=0)
                for label in unique_labels
            }

        # Step 1: Handle small clusters
        unique_labels, counts = np.unique(labels, return_counts=True)
        small_clusters = unique_labels[counts < small_cluster_count_thresh]

        if len(small_clusters) > 0 and merge_thresh > 0:
            logger.info(
                f"Found small clusters: {small_clusters}, these clusters have less than {small_cluster_count_thresh} samples."
            )
            centroids = get_centroids(labels, embeddings)
            cluster_centers = np.array([centroids[i] for i in range(max(labels) + 1)])

            new_labels = labels.copy()
            for i, label in enumerate(labels):
                if label in small_clusters:
                    similarities = cosine_similarity([embeddings[i]], cluster_centers)[
                        0
                    ]
                    valid_clusters = [
                        j for j in range(len(similarities)) if j not in small_clusters
                    ]
                    best_match = max(valid_clusters, key=lambda x: similarities[x])

                    if similarities[best_match] > merge_thresh:
                        new_labels[i] = best_match
                        logger.info(
                            f"Replaced small cluster {label} with {best_match}, score: {similarities[best_match]}"
                        )
                    else:
                        logger.info(
                            f"Kept small cluster {label}, as best match score: {similarities[best_match]} is too low."
                        )

            logger.info(f"step1, labels: {labels}, after_merge_small: {new_labels}")
            labels = new_labels

        # Step 2: Use merge_by_cos for global merging
        # labels = self.merge_by_cos(labels, embeddings, cos_thresh)
        # Step 3: Update centroids
        centroids = get_centroids(labels, embeddings)
        return labels, centroids

    def merge_by_cos(self, labels, embs, cos_thr):
        assert cos_thr > 0 and cos_thr <= 1
        while True:
            spk_num = labels.max() + 1
            if spk_num == 1:
                break
            spk_center = []
            for i in range(spk_num):
                spk_emb = embs[labels == i].mean(0)
                spk_center.append(spk_emb)
            assert len(spk_center) > 0
            spk_center = np.stack(spk_center, axis=0)
            norm_spk_center = spk_center / np.linalg.norm(
                spk_center, axis=1, keepdims=True
            )
            affinity = np.matmul(norm_spk_center, norm_spk_center.T)
            affinity = np.triu(affinity, 1)
            spks = np.unravel_index(np.argmax(affinity), affinity.shape)
            if affinity[spks] < cos_thr:
                break
            for i in range(len(labels)):
                if labels[i] == spks[1]:
                    labels[i] = spks[0]
                elif labels[i] > spks[1]:
                    labels[i] -= 1
        return labels


class SpeakerClustering:
    """
    This class only implements clustering on speaker embeddings get label ids.
    """

    def __init__(self, method="simple") -> None:
        self.method = method
        self.umap_hdbscan_cluster = UmapHdbscan()
        self.simple_clustering = SimpleClustering()

    def get_speaker_ids(
        self, embeddings, merge_threshold=0.35, batch_segments=100, debug=False
    ):
        if self.method == "simple":
            labels = self.simple_clustering(
                embeddings,
                merge_thresh=merge_threshold,
                batch_segments=batch_segments,
                debug=debug,
            )
        elif self.method == "funasr":
            labels = self.umap_hdbscan_cluster(embeddings)
            if merge_threshold > 0:
                labels = self.merge_by_cos(labels, embeddings, merge_threshold)
        return labels

    def merge_by_cos(self, labels, embs, cos_thr):
        # merge the similar speakers by cosine similarity
        assert cos_thr > 0 and cos_thr <= 1
        while True:
            spk_num = labels.max() + 1
            if spk_num == 1:
                break
            spk_center = []
            for i in range(spk_num):
                spk_emb = embs[labels == i].mean(0)
                spk_center.append(spk_emb)
            assert len(spk_center) > 0
            spk_center = np.stack(spk_center, axis=0)
            norm_spk_center = spk_center / np.linalg.norm(
                spk_center, axis=1, keepdims=True
            )
            affinity = np.matmul(norm_spk_center, norm_spk_center.T)
            affinity = np.triu(affinity, 1)
            spks = np.unravel_index(np.argmax(affinity), affinity.shape)
            if affinity[spks] < cos_thr:
                break
            for i in range(len(labels)):
                if labels[i] == spks[1]:
                    labels[i] = spks[0]
                elif labels[i] > spks[1]:
                    labels[i] -= 1
        return labels
