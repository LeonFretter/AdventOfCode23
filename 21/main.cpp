#include <memory>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <tuple>
#include <cstring>
#include <set>
#include <fstream>
#include <ctime>

struct Vec2 {
    int x;
    int y;
};

uint8_t countBits(uint8_t byte) {
    static const uint8_t NIBBLE_LOOKUP[16] = {
        0, 1, 1, 2, 1, 2, 2, 3,
        1, 2, 2, 3, 2, 3, 3, 4
    };

    return NIBBLE_LOOKUP[byte & 0x0F] + NIBBLE_LOOKUP[byte >> 4];
}


class Map {
public:
    int width() const { return w; }
    int height() const { return h; }

    bool get(Vec2 v) const {
        return get(v.x, v.y);
    }

    bool get(int x, int y) const {
        auto idx = byteIndex(x, y);
        if(idx >= elems.size()) {
            throw std::runtime_error("out of bounds");
        }
        return elems[idx] & (1 << (x % 8));
    }

    void set(int x, int y, bool value) {
        auto idx = byteIndex(x, y);
        if(idx >= elems.size()) {
            throw std::runtime_error("out of bounds");
        }
        if (value) {
            elems[idx] |= (1 << (x % 8));
        } else {
            elems[idx] &= ~(1 << (x % 8));
        }
    }

    int byteIndex(int x, int y) const {
        return y * w/8 + x/8;
    }

    int bitIndex(int x, int y) const {
        return x % 8;
    }

    void set(Vec2 v, bool value) {
        set(v.x, v.y, value);
    }

    std::vector<Vec2> neighbors(int x, int y) {
        auto res = std::vector<Vec2>{};
        res.reserve(4);
        auto minx = std::max(x-1, 0);
        auto miny = std::max(y-1, 0);
        auto maxx = std::min(x+1, w-1);
        auto maxy = std::min(y+1, h-1);

        for(auto i = minx; i <= maxx; i++) {
            for(auto j = miny; j <= maxy; j++) {
                if(i == x && j == y) {
                    continue;
                }
                if(i != x && j != y) {
                    continue;
                }
                res.push_back(Vec2{i, j});
            }
        }
        return res;
    }

    std::string stringify() {
        auto res = std::string{};
        for(auto y=0; y<h; ++y) {
            for(auto x=0; x<w; ++x) {
                res += (get(x, y) ? '#' : '.');
            }
            res += "\n";
        }
        return res;
    }

    explicit operator int() {
        int count = 0;
        for(auto elem: elems) {
            count += countBits(elem);
        }
        return count;
    }

    Map(int w, int h) : w(w), h(h) {
        auto bytes_needed = (w/8  + 1) * h * sizeof(char); 

        elems.resize(bytes_needed);
    }
    friend Map operator &(Map const& lhs, Map const& rhs) {
        auto res = Map{lhs.w, lhs.h};
        for (int i = 0; i < lhs.elems.size(); i++) {
            res.elems[i] = lhs.elems[i] & rhs.elems[i];
        }
        return res;
    }

    friend Map operator |(Map const& lhs, Map const& rhs) {
        auto res = Map{lhs.w, lhs.h};
        for(auto i=0; i<lhs.elems.size(); ++i) {
            res.elems[i] = lhs.elems[i] | rhs.elems[i];
        }
        return res;
    }
private:
    int w;
    int h;
    std::vector<char> elems;
};

void updateExtremeRow(std::pair<int, int>& row, int x) {
    if(row.first == -1) {
        row.first = x;
    }
    if(row.second == -1) {
        row.second = x;
    }
    row.first = std::min(row.first, x);
    row.second = std::max(row.second, x);
}

void updateExtremeColumn(std::pair<int, int>& col, int y) {
    if(col.first == -1) {
        col.first = y;
    }
    if(col.second == -1) {
        col.second = y;
    }
    col.first = std::min(col.first, y);
    col.second = std::max(col.second, y);
}

using ExtremeRow = std::pair<int, int>;
using ExtremeColumn = std::pair<int, int>;
using ExtremeRows = std::vector<ExtremeRow>;
using ExtremeColumns = std::vector<ExtremeColumn>;

void updateFromExtremeRows(Map& m, ExtremeRows const& current_rows, ExtremeRows& next_rows, ExtremeRows& next_cols) {
    auto y = 0;
    for(auto y = 0; y<current_rows.size(); ++y) {
        auto& row = current_rows[y];
        auto x1 = row.first;
        auto x2 = row.second;
        if(x1 == -1 && x2 == -1) {
            continue;
        }
        else {
            auto xs = std::set<int>{x1, x2};
            for(auto x : xs) {
                auto neighbors = m.neighbors(x, y);
                for(auto neighbor: neighbors) {
                    auto nx = neighbor.x;
                    auto ny = neighbor.y;

                    auto& extreme_row = next_rows[ny];
                    auto& extreme_col = next_rows[nx];
                    updateExtremeRow(extreme_row, nx);
                    updateExtremeColumn(extreme_col, ny);
                }

            }
        }
    }
}

void updateExtremeColumns(Map& m, ExtremeColumns const& current_cols, ExtremeColumns& next_cols, ExtremeRows& next_rows) {
    updateFromExtremeRows(m, current_cols, next_cols, next_rows);
}

Map mapFromExtremeRowsAndColumns(std::vector<std::pair<int, int>> const& extreme_row_xs, std::vector<std::pair<int, int>> const& extreme_col_ys) {
    auto m = Map{extreme_row_xs.size(), extreme_col_ys.size()};
    for(auto y=0; y<extreme_row_xs.size(); ++y) {
        auto& row = extreme_row_xs[y];
        auto xs = std::set<int>{row.first, row.second};
        for(auto x : xs) {
            if(x != -1) {
                m.set(x, y, true);
            }
        }
    }
    for(auto x=0; x<extreme_col_ys.size(); ++x) {
        auto& col = extreme_col_ys[x];
        auto ys = std::set<int>{col.first, col.second};
        for(auto y : ys) {
            if(y != -1) {
                m.set(x, y, true);
            }
        }
    }
    return m;
}

Map reachablePoints(Map m, Vec2 origin, int steps) {
    auto default_extreme_row_xs = std::vector<std::pair<int, int>>(m.height(), std::make_pair(-1, -1));
    auto default_extreme_col_ys = std::vector<std::pair<int, int>>(m.width(), std::make_pair(-1, -1));

    auto extreme_row_xs = default_extreme_row_xs;
    auto extreme_col_ys = default_extreme_col_ys;

    auto prev_m = m;
    m.set(origin.x, origin.y, true);
    extreme_row_xs[origin.y] = std::make_pair(origin.x, origin.x);
    extreme_col_ys[origin.x] = std::make_pair(origin.y, origin.y);

    for(auto i=0; i<steps; ++i) {
        auto next_extreme_row_xs = default_extreme_row_xs;
        auto next_extreme_col_ys = default_extreme_col_ys;

        updateFromExtremeRows(m, extreme_row_xs, next_extreme_row_xs, next_extreme_col_ys);
        updateExtremeColumns(m, extreme_col_ys, next_extreme_col_ys, next_extreme_row_xs);

        extreme_row_xs = next_extreme_row_xs;
        extreme_col_ys = next_extreme_col_ys;
        
        auto next_m = prev_m | mapFromExtremeRowsAndColumns(extreme_row_xs, extreme_col_ys);
        prev_m = m;
        m = next_m;

        if(i % 10 == 0) {
            std::cout << "step: " << i << std::endl;
        }
    }
    return m;
}

int main(int argc, char** argv) {
    auto example_m = Map{9, 9};
    auto example_origin = Vec2{4, 4};

    auto m1 = reachablePoints(example_m, example_origin, 1);
    std::cout << m1.stringify() << std::endl;
    auto m2 = reachablePoints(example_m, example_origin, 2);
    std::cout << m2.stringify() << std::endl;
    auto m3 = reachablePoints(example_m, example_origin, 3);
    std::cout << m3.stringify() << std::endl;

    auto t1 = time(nullptr);

    auto big_m = Map{2048, 2048};
    auto big_origin = Vec2{1024, 1024};
    big_m = reachablePoints(big_m, big_origin, 800);
    
    auto t2 = time(nullptr);
    std::cout << "time: " << t2 - t1 << std::endl;

    auto f = std::ofstream{"out.txt"};
    f << big_m.stringify();
}