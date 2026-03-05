class Bresenham:

    @staticmethod
    def find_path(start, finish, navigator):
        y0, x0 = start
        y1, x1 = finish
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        sy = 1 if y0 < y1 else -1
        sx = 1 if x0 < x1 else -1
        y, x = y0, x0
        if dx > dy:
            d = 2*dy - dx
            while True: 
                x += sx
                                       
                if y == y1 and x == x1:
                    return y0, x0 + sx
                if not navigator.valid((y, x)):
                    return None 
                if d >= 0:
                    y += sy   
                    if not navigator.valid((y, x)):
                        return None   
                    if y == y1 and x == x1:
                        return y0, x0 + sx
                    d -= 2*dx
                    
                d += 2*dy        
        else:        
            d = 2*dx - dy
            while True:
                y += sy               
                if y == y1 and x == x1:
                    return y0 + sy, x0
                if not navigator.valid((y, x)):
                    return None
                if d >= 0:
                    x += sx  
                    if y == y1 and x == x1:
                        return y0 + sy, x0 
                    if not navigator.valid((y, x)):
                        return None
                    d -= 2*dy  
                    
                d += 2*dx   