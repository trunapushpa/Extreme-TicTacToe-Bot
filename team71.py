import datetime
import random


class Team71:
    def __init__(self):
        self.startTime = datetime.datetime.utcnow()
        self.timeLimit = datetime.timedelta(seconds=14.9)
        self.default_depth = 3
        self.stopTime = False
        self.INF = 10000000000
        self.stored_board = {}
        self.zobrist = []
        self.hash_board = {}
        for i in xrange(16):
            self.zobrist.append([])
            for j in xrange(16):
                self.zobrist[i].append([])
                for k in xrange(2):
                    self.zobrist[i][j].append(random.randint(0, 0x10000000000000000L))
        # self.blockWeight = [[1, 2, 2, 1],
        #                     [2, 3, 3, 2],
        #                     [2, 3, 3, 2],
        #                     [1, 2, 2, 1]]
        self.dBlockWeight = [[6, 4, 4, 6],
                             [4, 3, 3, 4],
                             [4, 3, 3, 4],
                             [6, 4, 4, 6]]
        self.player_map = {}
        self.diamond_states = [[[0, 1], [1, 0], [1, 2], [2, 1]],
                               [[0, 2], [1, 1], [1, 3], [2, 2]],
                               [[1, 1], [2, 1], [2, 2], [3, 1]],
                               [[1, 2], [2, 1], [2, 3], [3, 2]]]
        self.score1 = 5000
        self.score2 = 100
        self.score3 = 5
        self.block_win_score = 100000
        self.block_lose_score = -100000

    def move(self, board, old_move, flag):
        # print('MyTurn')
        self.startTime = datetime.datetime.utcnow()
        self.stopTime = False
        if flag == 'x':
            self.player_map[True] = 'x'
            self.player_map[False] = 'o'
        else:
            self.player_map[True] = 'o'
            self.player_map[False] = 'x'
        retm = board.find_valid_move_cells(old_move)[0]
        bVal = -self.INF
        depth = self.default_depth
        while datetime.datetime.utcnow() - self.startTime < self.timeLimit:  # IDFS
            # print(depth)
            val, ret = self.ab_minimax(board, old_move, depth, True, -self.INF, self.INF)
            if not self.stopTime:
                bVal = val
                retm = ret
            # elif val > bVal:
            #     retm = ret
            depth += 1
        # print('MyTurn' + flag)
        return retm

    def ab_minimax(self, board, old_move, depth, my_chance, alpha, beta):
        children = board.find_valid_move_cells(old_move)
        bChild = children[random.randrange(len(children))]
        if my_chance:
            bestVal = -self.INF
            for child in children:
                if datetime.datetime.utcnow() - self.startTime > self.timeLimit:
                    self.stopTime = True
                    break
                board.update(old_move, child, self.player_map[True])
                bt = board.find_terminal_state()
                if bt[0] == 'CONTINUE':
                    if depth <= 0:
                        hash_value = 0
                        for i in xrange(16):
                            for j in xrange(16):
                                if board.board_status[i][j] != '-':
                                    if board.board_status[i][j] == self.player_map[True]:
                                        hash_value = hash_value ^ self.zobrist[i][j][0]
                                    else:
                                        hash_value = hash_value ^ self.zobrist[i][j][1]

                        if hash_value in self.hash_board:
                            # print "in Hash function"
                            # if my_chance:
                            val = self.hash_board[hash_value]
                            # else:
                            #     val = -self.hash_board[hash_value]
                        else:
                            val = self.heuristic(board)
                    else:
                        val = self.ab_minimax(board, child, depth - 1, False, alpha, beta)[0]
                    if val > bestVal:
                        bestVal = val
                        alpha = max(alpha, bestVal)
                        bChild = child
                    if beta <= alpha:
                        board.board_status[child[0]][child[1]] = '-'
                        board.block_status[child[0] // 4][child[1] // 4] = '-'
                        break
                elif bt[1] == 'WON' and bt[0] == self.player_map[True]:
                    board.board_status[child[0]][child[1]] = '-'
                    board.block_status[child[0] // 4][child[1] // 4] = '-'
                    # TODO: change INF to better value
                    return self.INF, child
                elif bt[1] == 'DRAW':
                    val = 0
                    for i in xrange(4):
                        for j in xrange(4):
                            if board.block_status[i][j] == self.player_map[True]:
                                val += self.dBlockWeight[i][j]
                            elif board.block_status[i][j] == self.player_map[False]:
                                val -= self.dBlockWeight[i][j]
                    # TODO: change values to something better
                    if val > 0:
                        val = 100000000 + (val * 1000)
                    else:
                        val = -100000000 + (val * 1000)
                    if val > bestVal:
                        bestVal = val
                        alpha = max(alpha, bestVal)
                        bChild = child
                    if beta <= alpha:
                        board.board_status[child[0]][child[1]] = '-'
                        board.block_status[child[0] // 4][child[1] // 4] = '-'
                        break
                # else:
                #     print("Something is fishy..")
                #     print(bt)
                board.board_status[child[0]][child[1]] = '-'
                board.block_status[child[0] // 4][child[1] // 4] = '-'
            return bestVal, bChild
        else:
            bestVal = self.INF
            for child in children:
                if datetime.datetime.utcnow() - self.startTime > self.timeLimit:
                    self.stopTime = True
                    break
                board.update(old_move, child, self.player_map[False])
                bt = board.find_terminal_state()
                if bt[0] == 'CONTINUE':
                    if depth <= 0:
                        hash_value = 0
                        for i in xrange(16):
                            for j in xrange(16):
                                if board.board_status[i][j] != '-':
                                    if board.board_status[i][j] == self.player_map[True]:
                                        hash_value = hash_value ^ self.zobrist[i][j][0]
                                    else:
                                        hash_value = hash_value ^ self.zobrist[i][j][1]

                        if hash_value in self.hash_board:
                            # print "in Hash function"
                            # if my_chance:
                            #     val = self.hash_board[hash_value]
                            # else:
                            val = self.hash_board[hash_value]
                        else:
                            val = self.heuristic(board)
                            self.hash_board[hash_value] = val
                    else:
                        val = self.ab_minimax(board, child, depth - 1, True, alpha, beta)[0]
                    if val < bestVal:
                        bestVal = val
                        beta = min(beta, bestVal)
                        bChild = child
                    if beta <= alpha:
                        board.board_status[child[0]][child[1]] = '-'
                        board.block_status[child[0] // 4][child[1] // 4] = '-'
                        break
                elif bt[1] == 'WON' and bt[0] == self.player_map[False]:
                    board.board_status[child[0]][child[1]] = '-'
                    board.block_status[child[0] // 4][child[1] // 4] = '-'
                    # TODO: change INF to better value
                    return (-1 * self.INF), child
                elif bt[1] == 'DRAW':
                    val = 0
                    for i in xrange(4):
                        for j in xrange(4):
                            if board.block_status[i][j] == self.player_map[True]:
                                val += self.dBlockWeight[i][j]
                            elif board.block_status[i][j] == self.player_map[False]:
                                val -= self.dBlockWeight[i][j]
                    # TODO: change values to something better
                    if val > 0:
                        val = 100000000 + (val * 1000)
                    else:
                        val = -100000000 + (val * 1000)
                    if val < bestVal:
                        bestVal = val
                        beta = min(beta, bestVal)
                        bChild = child
                    if beta <= alpha:
                        board.board_status[child[0]][child[1]] = '-'
                        board.block_status[child[0] // 4][child[1] // 4] = '-'
                        break
                # else:
                #     print("Something is fishy..")
                #     print(bt)
                board.board_status[child[0]][child[1]] = '-'
                board.block_status[child[0] // 4][child[1] // 4] = '-'
            return bestVal, bChild

    def heuristic(self, board):
        draw_score = 0

        for i in xrange(4):
            for j in range(4):
                temp_block = [[board.board_status[4 * i + k][4 * j + l] for l in range(0, 4)] for k in range(0, 4)]
                draw_score += (self.eval_block_score(temp_block)) * self.dBlockWeight[i][j]

        win_score = self.eval_block_score(board.block_status)

        # if win_score > 0:
        #     win_score = 10000000 + (win_score * 1000)
        # elif win_score < 0:
        #     win_score = -10000000 + (win_score * 1000)

        # if win_score != 0:
        #     print(win_score)
        # print(draw_score + (win_score * 100))
        return draw_score + win_score * 30

    def eval_block_score(self, block):

        t = tuple([tuple(block[i]) for i in range(4)])

        if t in self.stored_board:
            return self.stored_board[t]

        myBlockScore = 0
        oppBlockScore = 0

        # Check each block win case

        # Rows
        for i in xrange(4):
            # ith Row
            pct = 0
            opp = 0
            dct = 0
            for j in xrange(4):
                if block[i][j] == self.player_map[False]:
                    opp += 1
                elif block[i][j] == self.player_map[True]:
                    pct += 1
                elif block[i][j] == 'd':
                    dct += 1
            if opp == 0 and dct == 0:
                if pct == 4:
                    ret = self.block_win_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if pct == 3:  # 1 attack move
                    myBlockScore += self.score1
                elif pct == 2:  # 2 attack move
                    myBlockScore += self.score2
                elif pct == 1:  # 3 attack move
                    myBlockScore += self.score3
            elif pct == 0 and dct == 0:
                if opp == 4:
                    ret = self.block_lose_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if opp == 3:  # 1 attack move
                    oppBlockScore += self.score1
                elif opp == 2:  # 2 attack move
                    oppBlockScore += self.score2
                elif opp == 1:  # 3 attack move
                    oppBlockScore += self.score3

        # Cols
        for i in xrange(4):
            # ith Column
            pct = 0
            opp = 0
            dct = 0
            for j in xrange(4):
                if block[j][i] == self.player_map[False]:
                    opp += 1
                elif block[j][i] == self.player_map[True]:
                    pct += 1
                elif block[i][j] == 'd':
                    dct += 1
            if opp == 0 and dct == 0:
                if pct == 4:
                    ret = self.block_win_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if pct == 3:  # 1 attack move
                    myBlockScore += self.score1
                elif pct == 2:  # 2 attack move
                    myBlockScore += self.score2
                elif pct == 1:  # 3 attack move
                    myBlockScore += self.score3
            if pct == 0 and dct == 0:
                if opp == 4:
                    ret = self.block_lose_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if opp == 3:  # 1 attack move
                    oppBlockScore += self.score1
                elif opp == 2:  # 2 attack move
                    oppBlockScore += self.score2
                elif opp == 1:  # 3 attack move
                    oppBlockScore += self.score3

        # Diamonds
        for di in self.diamond_states:
            # ith Diamond
            pct = 0
            opp = 0
            dct = 0
            for cell in di:
                if block[cell[0]][cell[1]] == self.player_map[False]:
                    opp += 1
                elif block[cell[0]][cell[1]] == self.player_map[True]:
                    pct += 1
                elif block[cell[0]][cell[1]] == 'd':
                    dct += 1
            if opp == 0 and dct == 0:
                if pct == 4:
                    ret = self.block_win_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if pct == 3:  # 1 attack move
                    myBlockScore += self.score1
                elif pct == 2:  # 2 attack move
                    myBlockScore += self.score2
                elif pct == 1:  # 3 attack move
                    myBlockScore += self.score3
            if pct == 0 and dct == 0:
                if opp == 4:
                    ret = self.block_lose_score
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    block = zip(*block[::-1])
                    t = tuple([tuple(block[i]) for i in range(4)])
                    self.stored_board[t] = ret
                    return ret
                if opp == 3:  # 1 attack move
                    oppBlockScore += self.score1
                elif opp == 2:  # 2 attack move
                    oppBlockScore += self.score2
                elif opp == 1:  # 3 attack move
                    oppBlockScore += self.score3

        ret = myBlockScore - oppBlockScore
        self.stored_board[t] = ret
        block = zip(*block[::-1])
        t = tuple([tuple(block[i]) for i in range(4)])
        self.stored_board[t] = ret
        block = zip(*block[::-1])
        t = tuple([tuple(block[i]) for i in range(4)])
        self.stored_board[t] = ret
        block = zip(*block[::-1])
        t = tuple([tuple(block[i]) for i in range(4)])
        self.stored_board[t] = ret
        return ret
