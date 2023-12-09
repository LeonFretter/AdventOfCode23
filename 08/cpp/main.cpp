#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>

size_t getNodeNameHash(std::string const& str) {
    auto base = (size_t)'0';
    auto res = 0;

    res += ((size_t)str[0] - base);
    res += ((size_t)str[1] - base) << 8;
    res += ((size_t)str[2] - base) << 16;

    return res;
}

std::string getNodeName(size_t hash) {
    auto base = (size_t)'0';
    auto res = std::string{};
    res += (char)(base + (hash & 0xFF));
    res += (char)(base + ((hash >> 8) & 0xFF));
    res += (char)(base + ((hash >> 16) & 0xFF));

    return res;
}

struct Node {
    size_t hash;
    size_t lhs;
    size_t rhs;

    std::string name() const {
        return getNodeName(hash);
    }

    friend std::ostream& operator<<(std::ostream& os, Node const& n) {
        os << n.name() << " = (" << getNodeName(n.lhs) << ", " << getNodeName(n.rhs) << ")";
        return os;
    }

    bool operator==(Node const& other) const {
        return hash == other.hash && lhs == other.lhs && rhs == other.rhs;
    }
};

class Graph {
public:
    Node getNode(std::string const& name) {
        return getNode(getNodeNameHash(name));
    }

    Node getNode(size_t hash) {
        return nodes.at(hash);
    }

    Node goLeft(Node current) {
        return getNode(current.lhs);
    }

    Node goRight(Node current) {
        return getNode(current.rhs);
    }

    Node step(Node current, char instruction) {
        if(instruction == 'L') {
            return goLeft(current);
        } else if(instruction == 'R') {
            return goRight(current);
        } else {
            throw std::runtime_error("Invalid instruction");
        }
    }

    Graph(std::vector<Node> const& nodes) {
        for(auto& n : nodes) {
            this->nodes[n.hash] = n;
        }
    }

private:
    std::map<size_t, Node> nodes;
};

std::vector<std::string> split(std::string s, char delim) {
    auto ss = std::stringstream{s};
    auto res = std::vector<std::string>();
    auto segment = std::string{};
    while(std::getline(ss, segment, delim)) {
        res.push_back(segment);
    }
    return res;
}

std::string ltrim(std::string s, char c) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [c](char ch) {
        return ch != c;
    }));
    return s;
}

std::string rtrim(std::string s, char c) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [c](char ch) {
        return ch != c;
    }).base(), s.end());
    return s;
}

std::string trim(std::string s, char c) {
    return ltrim(rtrim(s, c), c);
}

Node readNode(std::string line) {
    auto parts = split(line, '=');
    for(auto& p : parts) {
            p = trim(p, ' ');
    }
    auto node_name = parts[0];

    if(node_name.size() != 3) {
        throw std::runtime_error("Invalid node name");
    }

    auto node_hash = getNodeNameHash(node_name);

    auto children = trim(trim(parts[1], '('), ')');
    auto children_parts = split(children, ',');
    for(auto& c : children_parts) {
        c = trim(c, ' ');
        if(c.size() != 3) {
            throw std::runtime_error("Invalid child node name");
        }
        std::cout << "child: " << c << std::endl;
    }

    auto lhs = getNodeNameHash(children_parts[0]);
    auto rhs = getNodeNameHash(children_parts[1]);

    return Node{node_hash, lhs, rhs};
}

class InstructionCircle {
public:
    char next() {
        auto res = instructions[idx];
        idx = (idx + 1) % instructions.size();
        return res;
    }

    InstructionCircle(std::string const& instructions, size_t idx = 0) : instructions(instructions), idx(idx) {}
private:
    std::string instructions;
    size_t idx;
};

struct Waypoint {
    Node node;
    Waypoint* child;
    size_t distance;
    Waypoint* next_destination;
};

class WaypointGraph {
public:
    WaypointGraph(std::string instructions, std::vector<Node> nodes, Graph graph)
        : instructions(instructions), nodes(nodes), graph(graph), waypoints()
     {
        waypoints.resize(instructions.size() * nodes.size());
        for(auto& wp : waypoints) {
            wp.node = Node{};
            wp.child = nullptr;
            wp.distance = -1;
            wp.next_destination = nullptr;
        }

        for(auto instruction_idx = 0UL; instruction_idx<instructions.size(); ++instruction_idx) {
            for(auto node_idx = 0UL; node_idx<nodes.size(); ++node_idx) {
                auto* wp = getWaypoint(instruction_idx, node_idx);
                wp->node = this->nodes[node_idx];
                auto next_instruction_idx = (instruction_idx + 1) % instructions.size();
                auto next_node = this->graph.step(wp->node, instructions[instruction_idx]);
                auto next_node_idx = std::distance(this->nodes.begin(), std::find(this->nodes.begin(), this->nodes.end(), next_node));
                wp->child = getWaypoint(next_instruction_idx, next_node_idx);
            }
        }

        auto set_waypoint_distances = 0UL;
        while(set_waypoint_distances < waypoints.size()) {
            std::cout << "Set waypoint distances: " << set_waypoint_distances << " of: " << waypoints.size() << std::endl;
            for(auto instruction_idx = 0UL; instruction_idx<instructions.size(); ++instruction_idx) {
                for(auto node_idx = 0UL; node_idx<nodes.size(); ++node_idx) {
                    auto* wp = getWaypoint(instruction_idx, node_idx);
                    if(wp->distance == -1) {
                        if(wp->node.name()[2] == 'Z') {
                            wp->distance = 0;
                            ++set_waypoint_distances;
                            wp->next_destination = wp;
                        } 
                        else if(wp->child->distance != -1) {
                            wp->distance = wp->child->distance + 1;
                            ++set_waypoint_distances;
                            wp->next_destination = wp->child->next_destination;
                        }
                    }
                }
            }
        }
    }

    Waypoint* getWaypoint(size_t instruction_idx, size_t node_idx) {
        return waypoints.data() + instruction_idx * nodes.size() + node_idx;
    }
    Waypoint const* getWaypoint(size_t instruction_idx, size_t node_idx) const {
        return waypoints.data() + instruction_idx * nodes.size() + node_idx;
    }

    Waypoint* getWaypoint(size_t instruction_idx, Node node) {
        return getWaypoint(instruction_idx, std::distance(nodes.begin(), std::find(nodes.begin(), nodes.end(), node)));
    }

private:
    std::string instructions;
    std::vector<Node> nodes;
    Graph graph;
    std::vector<Waypoint> waypoints;
};

struct Traversal {
    Waypoint* waypoint;
    size_t instruction_count;
};


int main(int argc, char** argv) {
    {
        auto trim_test = trim("  AAA  ", ' ');
        if(trim_test != "AAA") {
            throw std::runtime_error("Trim test failed");
        }

        auto test1 = getNodeName(getNodeNameHash("BBB"));
        if(test1 != "BBB") {
            throw std::runtime_error("Test 1 failed");
        }
        auto line1 = "DRM = (DLQ, BGR)";
        auto node1 = readNode(line1);
        if(node1.name() != "DRM" || node1.lhs != getNodeNameHash("DLQ") || node1.rhs != getNodeNameHash("BGR")) {
            throw std::runtime_error("Test 2 failed");
        }

        auto example_txt = R"(LR
11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
)";

        auto ss = std::stringstream{example_txt};
        auto line = std::string{};
        std::getline(ss, line);
        auto c = InstructionCircle{line};

        auto nodes = std::vector<Node>{};

        while(std::getline(ss, line)) {
            if(trim(line, ' ') != "") {
                nodes.push_back(readNode(line));
            }
        }
        if(nodes.size() != 8) {
            throw std::runtime_error("Test 3 failed: Not correct number of nodes");
        }

        auto g = Graph{nodes};

        auto start_nodes = std::vector<Node>{};
        std::copy_if(nodes.begin(), nodes.end(), std::back_inserter(start_nodes), [](Node n) {
            std::cout << n.name() << std::endl;
            return n.name()[2] == 'A';
        });

        if(start_nodes.size() != 2) {
            throw std::runtime_error("Test 3 failed: Not correct start nodes");
        }

        
    }


    auto fs = std::fstream{argv[1]};
    auto line = std::string{};
    std::getline(fs, line);
    auto instructions = line;
    auto c = InstructionCircle{line};

    auto nodes = std::vector<Node>{};
    while(std::getline(fs, line)) {
        if(trim(line, ' ') != "") {
            nodes.push_back(readNode(line));
        }
    }
    auto g = Graph{nodes};

    std::cout << "Nodes: " << std::endl;
    for(auto& n : nodes) {
        std::cout << n << std::endl;
    }

    auto is_dst_node = [](Node n) {
        return n.name()[2] == 'Z';
    };

    auto graph = WaypointGraph{instructions, nodes, g};

    auto start_nodes = std::vector<Node>{};
    std::copy_if(nodes.begin(), nodes.end(), std::back_inserter(start_nodes), [](Node n) {
        return n.name()[2] == 'A';
    });
    auto it_waypoints = std::vector<Waypoint*>{};
    std::transform(start_nodes.begin(), start_nodes.end(), std::back_inserter(it_waypoints), [&graph](Node n) {
        return graph.getWaypoint(0, n);
    });

    auto traversals = std::vector<Traversal>{};
    for(auto* wp : it_waypoints) {
        traversals.push_back(Traversal{wp, 0});
    }

    auto found = false;
    auto i = 0;
    while(!found) {
        if(std::all_of(traversals.begin(), traversals.end(), [&graph](Traversal t) {
            return t.waypoint->node.name()[2] == 'Z';
        })) {
            auto instruction_count = traversals[0].instruction_count;
            if(std::all_of(traversals.begin(), traversals.end(), [&instruction_count](Traversal t) {
                return t.instruction_count == instruction_count;
            })) {
                std::cout << "Part 2: " << instruction_count << std::endl;
                found = true;
                break;
            }
            else {
                std::sort(traversals.begin(), traversals.end(), [&instruction_count](Traversal t1, Traversal t2) {
                    return t1.instruction_count < t2.instruction_count;
                });
                auto& t = traversals[0];
                auto* next_child = t.waypoint->child;
                auto* next_wp = next_child->next_destination;
                auto dist = 1 + next_child->distance;
                t.instruction_count += dist;
                t.waypoint = next_wp;
            }
        } else {
            for(auto& t : traversals) {
                if(t.waypoint->node.name()[2] != 'Z') {
                    auto* next_child = t.waypoint->child;
                    auto* next_wp = next_child->next_destination;
                    auto dist = 1 + next_child->distance;
                    t.instruction_count += dist;
                    t.waypoint = next_wp;
                }
            }
        }
        i += 1;
        if(i % 100000 == 0) {
            std::cout << "min-count: " << traversals[0].instruction_count << std::endl;
        }
    }
    

    return EXIT_SUCCESS;
}