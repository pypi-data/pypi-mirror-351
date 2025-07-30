import cv2
import os
import sys
import json
import numpy as np
import time
from datetime import timedelta
from sklearn.cluster import KMeans
import skimage.metrics

def is_frame_blur(frame, threshold=100):
    """检测帧是否模糊（基于拉普拉斯方差）"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def compute_frame_similarity(frame1, frame2, method='ssim'):
    """计算两帧之间的相似度"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    if method == 'ssim':
        ssim_score = skimage.metrics.structural_similarity(gray1, gray2)
        return ssim_score
    
    elif method == 'orb':
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(gray1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)
        
        if des1 is None or des2 is None or des1.shape[0] == 0 or des2.shape[0] == 0:
            return 0.0
            
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        if len(matches) == 0:
            return 0.0
        return len(matches) / max(len(kp1), len(kp2), 1)
    
    elif method == 'histogram':
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    
    else:
        err = np.sum((gray1.astype("float") - gray2.astype("float")) ** 2)
        err /= float(gray1.shape[0] * gray1.shape[1])
        return 1 / (1 + err)

def compute_visual_diversity(frame1, frame2):
    """计算视觉多样性分数，综合多个指标"""
    ssim_score = compute_frame_similarity(frame1, frame2, 'ssim')
    hist_score = compute_frame_similarity(frame1, frame2, 'histogram')
    
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    edges1 = cv2.Canny(gray1, 50, 150)
    edges2 = cv2.Canny(gray2, 50, 150)
    
    edge_diff = np.sum(np.abs(edges1.astype(float) - edges2.astype(float)))
    edge_diff_norm = edge_diff / (frame1.shape[0] * frame1.shape[1] * 255)
    
    flow = cv2.calcOpticalFlowFarneback(
        gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
    )
    motion_magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean()
    
    hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
    
    hsv_diff = np.mean(np.abs(hsv1.astype(float) - hsv2.astype(float))) / 255.0
    
    diversity_score = (
        (1 - ssim_score) * 0.3 + 
        (1 - hist_score) * 0.2 + 
        edge_diff_norm * 0.2 + 
        min(motion_magnitude, 1.0) * 0.15 + 
        hsv_diff * 0.15
    )
    
    return diversity_score

def advanced_scene_detection(video_path, min_scene_duration=0.5, max_scene_duration=3.0):
    """使用多模态特征检测场景变化，增强场景边界检测"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None, None, None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    if duration < 15:
        min_scene_duration = 0.3
        max_scene_duration = 2.0
    elif duration < 30:
        min_scene_duration = 0.4
        max_scene_duration = 2.5
    
    scene_boundaries = [0]
    prev_frame = None
    similarity_threshold = 0.75
    motion_threshold = 0.03
    
    frame_similarities = []
    motion_levels = []
    diversity_scores = []
    
    ret, prev_frame = cap.read()
    if not ret:
        return None, None, None, None
    
    for frame_idx in range(1, total_frames):
        ret, frame = cap.read()
        if not ret:
            break
            
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, current_gray, None, 
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        motion = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean()
        
        similarity = compute_frame_similarity(prev_frame, frame, 'ssim')
        diversity = compute_visual_diversity(prev_frame, frame)
        
        frame_similarities.append(similarity)
        diversity_scores.append(diversity)
        
        current_scene_duration = (frame_idx - scene_boundaries[-1]) / fps
        
        scene_change_condition = (
            (similarity < similarity_threshold or diversity > 0.3) and 
            current_scene_duration > min_scene_duration and
            (motion > motion_threshold or diversity > 0.25)
        )
        
        if scene_change_condition:
            scene_boundaries.append(frame_idx)
        
        motion_levels.append(motion)
        prev_frame = frame
        
    scene_boundaries.append(total_frames - 1)
    cap.release()
    
    final_boundaries = optimize_scene_boundaries(
        scene_boundaries, fps, min_scene_duration, max_scene_duration
    )
    
    return final_boundaries, fps, motion_levels, diversity_scores

def optimize_scene_boundaries(boundaries, fps, min_duration, max_duration):
    """优化场景边界，合并过短场景，拆分过长场景"""
    final_boundaries = [boundaries[0]]
    min_frames = int(fps * min_duration)
    max_frames = int(fps * max_duration)
    
    for i in range(1, len(boundaries)):
        scene_length = boundaries[i] - final_boundaries[-1]
        
        if scene_length < min_frames and i < len(boundaries) - 1:
            continue
        
        elif scene_length > max_frames:
            splits = max(2, scene_length // max_frames + 1)
            split_size = scene_length // splits
            for j in range(1, splits):
                final_boundaries.append(final_boundaries[-1] + split_size)
        
        final_boundaries.append(boundaries[i])
    
    return final_boundaries

def select_diverse_frames_advanced(frames, frame_indices, max_frames=6, 
                                  diversity_threshold=0.35, blur_threshold=100):
    """使用高级算法选择视觉上最多样化的帧（跳过模糊帧）"""
    if len(frames) <= max_frames:
        return list(range(len(frames)))
    
    features = []
    clear_frames = []
    clear_indices = []
    
    for idx, frame in enumerate(frames):
        if is_frame_blur(frame, blur_threshold):
            continue
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        hist_h = cv2.calcHist([hsv], [0], None, [8], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [8], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [8], [0, 256])
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        texture_energy = np.mean(np.sqrt(sobel_x**2 + sobel_y**2))
        
        feature = np.concatenate([
            cv2.normalize(hist_h, None).flatten(),
            cv2.normalize(hist_s, None).flatten(),
            cv2.normalize(hist_v, None).flatten(),
            [edge_density, texture_energy / 255.0]
        ])
        features.append(feature)
        clear_frames.append(frame)
        clear_indices.append(frame_indices[idx])
    
    if not clear_frames:
        return []
    
    features = np.array(features)
    
    n_clusters = min(max_frames * 2, len(clear_frames))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(features)
    
    candidate_indices = []
    for i in range(n_clusters):
        cluster_mask = kmeans.labels_ == i
        if not np.any(cluster_mask):
            continue
            
        cluster_indices = np.where(cluster_mask)[0]
        cluster_center = kmeans.cluster_centers_[i]
        cluster_features = features[cluster_mask]
        
        distances = np.linalg.norm(cluster_features - cluster_center, axis=1)
        closest_local_idx = np.argmin(distances)
        closest_global_idx = cluster_indices[closest_local_idx]
        candidate_indices.append(closest_global_idx)
    
    if len(candidate_indices) <= max_frames:
        return [clear_indices[idx] for idx in candidate_indices]
    
    selected = [candidate_indices[0]]
    candidates = candidate_indices[1:]
    
    while len(selected) < max_frames and candidates:
        best_candidate = None
        best_diversity = -1
        
        for candidate in candidates:
            min_diversity = float('inf')
            for selected_idx in selected:
                diversity = compute_visual_diversity(
                    clear_frames[selected_idx], 
                    clear_frames[candidate]
                )
                min_diversity = min(min_diversity, diversity)
            
            if min_diversity > best_diversity:
                best_diversity = min_diversity
                best_candidate = candidate
        
        if best_candidate is not None and best_diversity > diversity_threshold:
            selected.append(best_candidate)
            candidates.remove(best_candidate)
        else:
            if candidates:
                selected.append(candidates[0])
                candidates.remove(candidates[0])
    
    return [clear_indices[idx] for idx in sorted(selected)]

def extract_diverse_frames(video_path, output_folder, max_frames_per_scene=5, 
                          global_diversity_check=True, blur_threshold=100):
    """提取多样化的帧序列，严格避免视觉重复和模糊帧"""
    os.makedirs(output_folder, exist_ok=True)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    boundaries, fps, motion_levels, diversity_scores = advanced_scene_detection(video_path)
    if boundaries is None or len(boundaries) < 2:
        boundaries = [0, total_frames-1]
    
    scene_data = []
    frame_counter = 1
    all_extracted_frames = []
    
    for i in range(len(boundaries) - 1):
        start_frame = boundaries[i]
        end_frame = boundaries[i + 1]
        scene_frames = end_frame - start_frame
        scene_duration = scene_frames / fps
        
        if scene_duration < 0.2:
            continue
        
        scene_id = i + 1
        start_time = start_frame / fps
        end_time = end_frame / fps
        
        scene_info = {
            "scene_id": int(scene_id),
            "start_time": float(start_time),
            "end_time": float(end_time),
            "duration": float(scene_duration),
            "start_frame": int(start_frame),
            "end_frame": int(end_frame),
            "key_frames": [],
            "description": f"场景{scene_id} (时长: {scene_duration:.1f}秒)"
        }
        
        if scene_duration < 1.0:
            sample_step = max(1, scene_frames // 20)
        elif scene_duration < 3.0:
            sample_step = max(1, scene_frames // 30)
        else:
            sample_step = max(1, scene_frames // 40)
        
        scene_frame_list = []
        frame_indices = []
        
        for frame_idx in range(start_frame, end_frame, sample_step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            if is_frame_blur(frame, blur_threshold):
                continue
                
            scene_frame_list.append(frame)
            frame_indices.append(frame_idx)
        
        if len(scene_frame_list) < 2:
            continue
        
        scene_max_frames = min(max_frames_per_scene, max(2, int(scene_duration * 2)))
        
        selected_indices = select_diverse_frames_advanced(
            scene_frame_list, frame_indices, 
            max_frames=scene_max_frames,
            diversity_threshold=0.4,
            blur_threshold=blur_threshold
        )
        
        scene_extracted_frames = []
        for idx in selected_indices:
            frame_idx = idx
            frame = scene_frame_list[frame_indices.index(idx)]
            
            if global_diversity_check and all_extracted_frames:
                is_diverse_globally = True
                for prev_frame in all_extracted_frames[-10:]:
                    diversity = compute_visual_diversity(prev_frame, frame)
                    if diversity < 0.3:
                        is_diverse_globally = False
                        break
                
                if not is_diverse_globally:
                    continue
            
            timestamp = frame_idx / fps
            time_str = str(timedelta(seconds=timestamp)).replace(':', '-')
            display_frame = frame.copy()
            cv2.putText(
                display_frame, 
                f"{time_str}s", 
                (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 255, 255), 
                2
            )
            
            filename = f"{video_name}_scene{scene_id:03d}_frame{frame_counter:04d}_{time_str}.jpg"
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, display_frame)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            scene_info["key_frames"].append({
                "file": filename,
                "timestamp": float(timestamp),
                "frame_index": int(frame_idx),
                "motion_level": float(motion_levels[frame_idx-1]) if frame_idx-1 < len(motion_levels) else 0.0,
                "diversity_score": float(diversity_scores[frame_idx-1]) if frame_idx-1 < len(diversity_scores) else 0.0,
                "sharpness": float(sharpness)
            })
            
            all_extracted_frames.append(frame)
            scene_extracted_frames.append(frame)
            frame_counter += 1
        
        if scene_info["key_frames"]:
            scene_data.append(scene_info)
    
    cap.release()
    
    metadata_path = os.path.join(output_folder, "scene_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            "video_info": {
                "filename": os.path.basename(video_path),
                "duration": float(duration),
                "fps": float(fps),
                "total_frames": int(total_frames),
                "extracted_frames": int(frame_counter - 1),
                "processing_settings": {
                    "max_frames_per_scene": int(max_frames_per_scene),
                    "global_diversity_check": bool(global_diversity_check),
                    "diversity_threshold": 0.4,
                    "blur_threshold": blur_threshold
                }
            },
            "scenes": scene_data
        }, f, ensure_ascii=False, indent=2)
    
    return True
