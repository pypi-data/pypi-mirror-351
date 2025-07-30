import os
import sys
import argparse
import glob
import time
from .core import extract_diverse_frames, is_frame_blur

def process_videos(input_path, output_root, max_frames=5, blur_threshold=100):
    """处理短视频文件或目录"""
    os.makedirs(output_root, exist_ok=True)
    
    if os.path.isfile(input_path):
        video_name = os.path.splitext(os.path.basename(input_path))[0]
        output_folder = os.path.join(output_root, video_name)
        return extract_diverse_frames(input_path, output_folder, max_frames, 
                                    True, blur_threshold)
    
    elif os.path.isdir(input_path):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.ts']
        processed_count = 0
        
        for ext in video_extensions:
            for video_path in glob.glob(os.path.join(input_path, f"*{ext}")):
                print(f"\n{'='*60}")
                print(f"处理视频: {os.path.basename(video_path)}")
                print(f"{'='*60}")
                
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_folder = os.path.join(output_root, video_name)
                
                try:
                    if extract_diverse_frames(video_path, output_folder, max_frames, 
                                            True, blur_threshold):
                        processed_count += 1
                except Exception as e:
                    print(f"处理失败: {e}")
        
        print(f"\n批量处理完成! 共成功处理 {processed_count} 个视频")
        return processed_count > 0
    
    else:
        print(f"错误: 无效路径 '{input_path}'")
        return False

def check_dependencies():
    """检查必要的依赖"""
    try:
        import cv2
        import skimage
        import sklearn
        print("依赖检查通过")
        return True
    except ImportError as e:
        print(f"依赖错误: {e}")
        print("请安装以下必要依赖:")
        print("  pip install opencv-python scikit-image scikit-learn")
        return False

def main():
    print("高级视频帧提取工具 v2.0 - 智能去重版")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
        
    parser = argparse.ArgumentParser(
        description='高级视频帧提取工具 - 智能减少视觉重复',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_path', help='视频文件或目录路径')
    parser.add_argument('-o', '--output', default='diverse_frames_v2', 
                        help='输出根目录 (默认: diverse_frames_v2)')
    parser.add_argument('-m', '--max', type=int, default=5,
                        help='每个场景最大帧数 (默认: 5，推荐3-6)')
    parser.add_argument('--no-global-check', action='store_true',
                        help='禁用全局多样性检查 (加快处理速度)')
    parser.add_argument('--blur-threshold', type=int, default=100,
                        help='模糊检测阈值 (默认: 100，值越小越严格)')
    
    args = parser.parse_args()
    
    print(f"输入路径: {args.input_path}")
    print(f"输出目录: {args.output}")
    print(f"每场景最大帧数: {args.max}")
    print(f"全局多样性检查: {'关闭' if args.no_global_check else '开启'}")
    print(f"模糊检测阈值: {args.blur_threshold}")
    print("-" * 50)
    
    start_time = time.time()
    success = process_videos(
        args.input_path, 
        args.output, 
        args.max,
        args.blur_threshold
    )
    end_time = time.time()
    
    print(f"\n总耗时: {end_time - start_time:.1f} 秒")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
