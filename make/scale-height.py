#!/usr/bin/env python3
import sys
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform

def scale_font(input_path, output_path, scale_y=0.9, scale_x=1.0):
    font = TTFont(input_path)

    # glyf 테이블 변형 (TrueType)
    if 'glyf' in font:
        glyf = font['glyf']

        for glyph_name in font.glyphOrder:
            if glyph_name not in glyf:
                continue

            glyph = glyf[glyph_name]

            # 컴포지트 글리프 처리
            if glyph.isComposite():
                for component in glyph.components:
                    # 컴포넌트의 변환 매트릭스 조정
                    if hasattr(component, 'x') and hasattr(component, 'y'):
                        component.x = int(component.x * scale_x)
                        component.y = int(component.y * scale_y)

                    # transform 매트릭스가 있는 경우
                    if hasattr(component, 'transform'):
                        # 2x2 변환 매트릭스: [[xx, xy], [yx, yy]]
                        t = component.transform
                        if len(t) >= 4:
                            # X 스케일링
                            t[0] = t[0] * scale_x  # xx
                            t[2] = t[2] * scale_x  # yx
                            # Y 스케일링
                            t[1] = t[1] * scale_y  # xy
                            t[3] = t[3] * scale_y  # yy
                        if len(t) >= 6:
                            # 이동 성분
                            t[4] = int(t[4] * scale_x)  # dx
                            t[5] = int(t[5] * scale_y)  # dy

            # 단순 글리프 처리 (좌표 직접 변형)
            elif hasattr(glyph, 'coordinates'):
                if glyph.coordinates:
                    coords = glyph.coordinates
                    # GlyphCoordinates 객체의 배열 수정
                    for i in range(len(coords)):
                        x, y = coords[i]
                        coords[i] = (int(x * scale_x), int(y * scale_y))

    # CFF 테이블 변형 (OpenType/CFF) - 필요시
    elif 'CFF ' in font or 'CFF2' in font:
        print("Warning: CFF font scaling not fully implemented")
        # CFF 폰트는 더 복잡한 처리가 필요

    # 메트릭스 조정
    if 'hmtx' in font:
        hmtx = font['hmtx']
        for glyph_name in hmtx.metrics.keys():
            width, lsb = hmtx.metrics[glyph_name]
            hmtx.metrics[glyph_name] = (int(width * scale_x), int(lsb * scale_x))

    # 전역 메트릭스 조정
    if 'head' in font:
        head = font['head']
        head.yMin = int(head.yMin * scale_y)
        head.yMax = int(head.yMax * scale_y)
        head.xMin = int(head.xMin * scale_x)
        head.xMax = int(head.xMax * scale_x)

    if 'OS/2' in font:
        os2 = font['OS/2']
        os2.sTypoAscender = int(os2.sTypoAscender * scale_y)
        os2.sTypoDescender = int(os2.sTypoDescender * scale_y)
        os2.sTypoLineGap = int(os2.sTypoLineGap * scale_y * 0.8)

        if hasattr(os2, 'usWinAscent'):
            os2.usWinAscent = int(os2.usWinAscent * scale_y)
        if hasattr(os2, 'usWinDescent'):
            os2.usWinDescent = int(os2.usWinDescent * scale_y)
        if hasattr(os2, 'sCapHeight'):
            os2.sCapHeight = int(os2.sCapHeight * scale_y)
        if hasattr(os2, 'sxHeight'):
            os2.sxHeight = int(os2.sxHeight * scale_y)

    if 'hhea' in font:
        hhea = font['hhea']
        hhea.ascent = int(hhea.ascent * scale_y)
        hhea.descent = int(hhea.descent * scale_y)
        hhea.lineGap = int(hhea.lineGap * scale_y * 0.8)

    # bounds 재계산
    font.recalcBBoxes = True

    font.save(output_path)
    font.close()
    print(f"✓ Scaled: {input_path} → {output_path} (X={scale_x}, Y={scale_y})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scale-height.py input.ttf output.ttf [scale_y] [scale_x]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    scale_y = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
    scale_x = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

    scale_font(input_file, output_file, scale_y, scale_x)