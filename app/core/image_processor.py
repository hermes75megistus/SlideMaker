# app/core/image_processor.py
from PIL import Image

class ImageProcessor:
    """
    Görüntü işleme fonksiyonlarını sağlayan sınıf
    """
    
    def __init__(self):
        pass
    
    def resize_image_with_custom_crop(self, img, width, height, center_x=None, center_y=None):
        """
        Görüntüyü belirli bir boyuta yeniden boyutlandırır ve özel bir kırpma noktası kullanır
        
        Args:
            img: PIL Image nesnesi
            width: Hedef genişlik
            height: Hedef yükseklik
            center_x: Kırpma merkezi X koordinatı (0-1 aralığında)
            center_y: Kırpma merkezi Y koordinatı (0-1 aralığında)
            
        Returns:
            Yeniden boyutlandırılmış ve kırpılmış PIL Image nesnesi
        """
        # Orijinal boyutları al
        original_width, original_height = img.size
        
        # En boy oranlarını hesapla
        target_ratio = width / height
        original_ratio = original_width / original_height
        
        # Debug bilgisi
        print(f"Crop center: x={center_x}, y={center_y}")
        print(f"Original size: {original_width}x{original_height}, ratio: {original_ratio}")
        print(f"Target size: {width}x{height}, ratio: {target_ratio}")
        
        if original_ratio > target_ratio:
            # Görüntü hedeften daha geniş - yükseklikle eşleştir ve genişliği kırp
            new_height = height
            new_width = int(new_height * original_ratio)
            resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            print(f"Image is wider, resized to: {new_width}x{new_height}")
            
            # Kırpma boyutlarını hesapla
            if center_x is not None:
                # Kırpma merkezi oranını piksel konumuna dönüştür
                # Yeniden boyutlandırılmış görüntü üzerindeki konumu ölçekle
                scaled_center_x = int(center_x * new_width)
                
                # Kırpmanın sol kenarını hesapla (ortalanmış bir kırpma için kaydırma)
                left = scaled_center_x - (width // 2)
                
                # Kırpma alanının sınırlar içinde olduğundan emin ol
                left = max(0, min(left, new_width - width))
                right = left + width
                
                print(f"Custom crop: x={scaled_center_x}, left={left}, right={right}")
            else:
                # Varsayılan merkezi kırpma
                left = (new_width - width) // 2
                right = left + width
                print(f"Default center crop: left={left}, right={right}")
                
            top = 0
            bottom = height
            
        else:
            # Görüntü hedeften daha uzun - genişlikle eşleştir ve yüksekliği kırp
            new_width = width
            new_height = int(new_width / original_ratio)
            resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            print(f"Image is taller, resized to: {new_width}x{new_height}")
            
            # Kırpma boyutlarını hesapla
            if center_y is not None:
                # Kırpma merkezi oranını piksel konumuna dönüştür
                # Yeniden boyutlandırılmış görüntü üzerindeki konumu ölçekle
                scaled_center_y = int(center_y * new_height)
                
                # Kırpmanın üst kenarını hesapla (ortalanmış bir kırpma için kaydırma)
                top = scaled_center_y - (height // 2)
                
                # Kırpma alanının sınırlar içinde olduğundan emin ol
                top = max(0, min(top, new_height - height))
                bottom = top + height
                
                print(f"Custom crop: y={scaled_center_y}, top={top}, bottom={bottom}")
            else:
                # Varsayılan merkezi kırpma
                top = (new_height - height) // 2
                bottom = top + height
                print(f"Default center crop: top={top}, bottom={bottom}")
                
            left = 0
            right = width
        
        # Kırpma işlemini gerçekleştir
        cropped = resized.crop((left, top, right, bottom))
        print(f"Final cropped size: {cropped.size}")
        return cropped
