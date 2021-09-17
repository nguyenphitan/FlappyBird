#import thư viện: pygame, random, ...
from math import fabs, pi
import pygame, random, sys
from pygame.locals import *     

# khởi tạo tất cả các modul cần thiết cho pygame (hoặc pygame.init())
pygame.init()
clock = pygame.time.Clock()     # Mục tiêu là có thể đặt FPS cố định giúp trò chơi chạy ở cùng tốc độ trên máy tính nhanh hay chậm.
fps = 32
screenWidth = 289
screenHeight = 511
screen = pygame.display.set_mode((screenWidth, screenHeight))
groundy = screenHeight * 0.8    # vị trí tối đa để đặt các items
Items = {}
sounds = {}
bird = 'items/bird.png'
background = 'items/background.png'
pipe = 'items/pipe.png'

def init():
    # Thêm các số vào list Items
    Items['numbers'] = {
        pygame.image.load('items/0.png').convert_alpha(),
        pygame.image.load('items/1.png').convert_alpha(),
        pygame.image.load('items/2.png').convert_alpha(),
        pygame.image.load('items/3.png').convert_alpha(),
        pygame.image.load('items/4.png').convert_alpha(),
        pygame.image.load('items/5.png').convert_alpha(),
        pygame.image.load('items/6.png').convert_alpha(),
        pygame.image.load('items/7.png').convert_alpha(),
        pygame.image.load('items/8.png').convert_alpha(),
        pygame.image.load('items/9.png').convert_alpha()
    }

    # Thêm các hình ảnh vào list Items
    Items['background'] = pygame.image.load(background).convert_alpha()
    Items['bird'] = pygame.image.load(bird).convert_alpha()
    Items['mess'] = pygame.image.load('items/message.png').convert_alpha()
    Items['path'] = pygame.image.load('items/base.png').convert_alpha()
    Items['pipe'] = ( pygame.transform.rotate(pygame.image.load(pipe).convert_alpha() , 180),  # quay ngược ống 180 độ để được ống phía trên
    pygame.image.load(pipe).convert_alpha() )

    # Thêm các âm thanh vào list sounds
    sounds['die'] = pygame.mixer.Sound('audios/die.wav')    # âm thanh khi rơi
    sounds['hit'] = pygame.mixer.Sound('audios/hit.wav')    # âm thanh khi va chạm
    sounds['point'] = pygame.mixer.Sound('audios/point.wav')    # âm thanh cộng điểm khi vượt qua chướng ngại vật
    sounds['swoosh'] = pygame.mixer.Sound('audios/swoosh.wav') 
    sounds['wing'] = pygame.mixer.Sound('audios/wing.wav')  # âm thanh khi con chim bay lên


def screenDisplay():
    # Hiện ra các hình ảnh khi mới vào game
    birdx = int(screenWidth/5)
    birdy = int((screenHeight - Items['bird'].get_height()) / 2)
    messx = int((screenWidth - Items['mess'].get_width()) / 2)
    messy = int(screenHeight * 0.13)
    pathx = 0

    screen.blit( Items['background'] , (0, 0) )
    screen.blit( Items['bird'], (birdx, birdy) )
    # screen.blit( Items['mess'], (messx, messy) )
    screen.blit( Items['path'], (pathx, groundy) )  # pathy = groundy
    pygame.display.update()
    clock.tick(fps)


def setUpScreen():
    while True:
        for event in pygame.event.get():    # nắm bắt các sự kiện mà người dùng tác động vào
            # nếu người dùng ấn nút thoát (X) hoặc esc thì đóng cửa sổ game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()  # Thoát khỏi console trong python
            
            # Khi người dùng ấn phím space hoặc nút lên thì kết thúc hàm welcome
            # Bắt đầu chơi
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            
            # Hiện lên các hình ảnh đầu game
            else:
                screenDisplay()
                


# Viết hàm tạo random các ống (pipe) trên - dưới:
def getRandomPipe():
    # Lấy ra chiều cao của ống
    pipeHeight = Items['pipe'][0].get_height()  # get_height() : trả về chiều cao tính bằng pixel
    offset = screenHeight / 3  # Khoảng cách giữa 2 ống đối diện là offset##
    
    # Thiết lập chiều cao của ống phía dưới (toạ độ y)
    pipeBottomHeight = offset + random.randrange( 0 , int( screenHeight - Items['path'].get_height() - 1.2*offset ) )

    # Thiết lập chiều cao của ống phía trên (toạ độ y)
    pipeTopHeight = pipeBottomHeight - offset - pipeHeight

    # Khởi tạo vị trí cho ống đầu tiên  (toạn độ x)
    pipex = screenWidth + 10

    # Thêm hai ống trên + dưới vào thành một pipe hoàn chỉnh
    pipe = [
        {'x' : pipex , 'y' : pipeTopHeight},   # ống trên
        {'x' : pipex , 'y' : pipeBottomHeight}    # ống dưới
    ]

    return pipe


# Viết hàm kiểm tra va chạm
def checkColide(birdx , birdy, topPipes, bottomPipes):
    '''
        birdx, birdy : toạ độ của bird
    '''

    # Nếu bird cao hơn đường (path) hoặc thấp hơn 0
    # Thì thông báo va chạm
    if birdy > screenHeight - 25 or birdy < 0:
        sounds['hit'].play() # phát âm thanh 
        return True
    
    # Duyệt các ống phía trên, nếu chiều cao của bird < chiều cao ống trên
    # và vị trí của bird đang nằm trong khoảng chiều rộng (width) của ống
    # thì thông báo va chạm
    for pipe in topPipes:
        pipeHeight = Items['pipe'][0].get_height()  #####
        if birdy < pipeHeight + pipe['y'] and abs(birdx - pipe['x']) < Items['pipe'][0].get_width():
            sounds['hit'].play()
            return True
    
    # Tương tự duyệt các ống phía dưới
    for pipe in bottomPipes:
        if birdy + Items['bird'].get_height() > pipe['y'] and abs(birdx - pipe['x']) < Items['pipe'][1].get_width():
            sounds['hit'].play()
            return True
    
    return False


def mainGame(): # xử lý nghiệp vụ khi chơi game
    score = 0  # Khởi tạo điểm số
    birdx = int(screenWidth/5)   # Khởi tạo vị trí (x,y) của bird
    birdy = int(screenHeight/2)
    pathx = 0   # Khởi tạo vị trí của path

    # Tạo hai ống có chiều cao ngẫu nhiên
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Tạo danh sách các đường ống phía trên ( Sẽ lấy 2,... ống xuất hiện trên màn hình, tuỳ sở thích )
    topPipes = [
        {'x' : screenWidth + 200 , 'y' : newPipe1[0]['y']},
        {'x' : screenWidth + 200 + (screenWidth/2) , 'y' : newPipe2[0]['y']}
        # Khoảng cách giữa 2 ống = screenWidth / 2
    ]

    # Tạo danh sách các đường ống phía dưới ( Sẽ lấy 2,... ống xuất hiện trên màn hình, tuỳ sở thích )
    bottomPipes = [
        {'x' : screenWidth + 200 , 'y' : newPipe1[1]['y']},
        {'x' : screenWidth + 200 + (screenWidth/2) , 'y' : newPipe2[1]['y']}
    ]

    pipeVelX = -4
    birdVelY = -9
    birdMinVelY = -8
    birdMaxVelY = 10
    birdAccy = 1

    birdFlap = -8   # Vận tốc bay lên khi vỗ cánh
    flapped = False # Kiểm tra có đang vỗ cánh hay không

    while True:
        # Kiểm tra sự kiện như trên
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # Lên nhạc :))
                if birdy > 0:
                    birdVelY = birdFlap
                    flapped = True  # Đã vỗ cánh
                    sounds['wing'].play()
    
        # Kiểm tra va chạm
        if checkColide(birdx , birdy, topPipes, bottomPipes):
            return
        
        # Tính điểm và hiển thị điểm
        birdMid = birdx + Items['bird'].get_width()/2   # vị trí giữa của bird
        # Duyệt các ống
        # Khi bird bay qua giữa ống thì bắt đầu cộng điểm, lên nhạc
        for pipe in topPipes:
            pipeMid = pipe['x'] + Items['pipe'][0].get_width()/2    # vị trí giữa của ống
            if pipeMid <= birdMid < pipeMid + 4:
                score += 1
                print(f"Điểm của bạn là: {score}")
                sounds['point'].play()
        
        # Nếu chưa vỗ cánh ....
        if flapped == False and birdVelY < birdMaxVelY:
            birdVelY += birdAccy
        
        # Nếu vỗ cánh
        if flapped:
            flapped = False
        # Update vị trí mới cho bird
        birdHeight = Items['bird'].get_height()
        birdy = birdy + min(birdVelY , groundy - birdy - birdHeight)

        # Di chuyển các đường ống sang trái
        for top, bot in zip(topPipes , bottomPipes):
            top['x'] += pipeVelX
            bot['x'] += pipeVelX
        
        # Thêm một đường ống mới khi ống cũ sắp vượt ra khỏi màn hình
        if 0 < topPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            topPipes.append(newPipe[0])
            bottomPipes.append(newPipe[1])
        
        # Nếu ống ra khỏi màn hình thì xoá ống
        if topPipes[0]['x'] < -Items['pipe'][0].get_width():
            topPipes.pop(0)
            bottomPipes.pop(0)
        
        # Tiếp tục hiển thị các hình ảnh
        screen.blit(Items['background'] , (0,0))
        for top, bot in zip(topPipes, bottomPipes):
            screen.blit( Items['pipe'][0] , ( top['x'] , top['y'] ) )
            screen.blit( Items['pipe'][1] , ( bot['x'] , bot['y'] ) )

        screen.blit(Items['path'] , (0 , groundy))
        screen.blit(Items['bird'] , (birdx , birdy))
        # countArr = [int(i) for i in list(str(score))]
        # width = 0   # chiều rông (chiếm chỗ) của điểm số
        # for i in countArr:
        #     width = width + Items['numbers'][i].get_width()
        # xoffset = ( screenWidth - width ) / 2

        # for i in countArr:
        #     screen.blit(Items['numbers'][i] , (xoffset , screenHeight*0.12))
        #     xoffset += Items['numbers'][i].get_width()
        
        pygame.display.update()
        clock.tick(fps)
        


if __name__ == "__main__":
    pygame.display.set_caption('Nhóm 5 - Flappy Bird')
    init()
    while True:
        setUpScreen()
        mainGame()







