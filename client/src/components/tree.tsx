import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface TreeNode {
  name: string;
  children?: TreeNode[];
}

let treeDict = {
    "type": "tree",
    "result": [
        {
            "explanation": "Designing a data structure for real-time ticket bookings involves several key components.",
            "tree": {
                "name": "Ticket Booking System",
                "children": [
                    {
                        "name": "Data Structures",
                        "children": [
                            {
                                "name": "Queue",
                                "children": [
                                    {
                                        "name": "For handling waiting customers",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "Hash Map",
                                "children": [
                                    {
                                        "name": "For quick access to booked tickets",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "Binary Search Tree",
                                "children": [
                                    {
                                        "name": "For managing seat availability",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Key Functions",
                        "children": [
                            {
                                "name": "Book Ticket",
                                "children": []
                            },
                            {
                                "name": "Cancel Ticket",
                                "children": []
                            },
                            {
                                "name": "Check Availability",
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "Concurrency Management",
                        "children": [
                            {
                                "name": "Locks or Semaphores",
                                "children": [
                                    {
                                        "name": "To ensure thread-safety",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    ]
}

const TreeGraph: React.FC = () => {
  const d3Container = useRef<SVGSVGElement | null>(null);
  const data: TreeNode = treeDict.result[0].tree;

  useEffect(() => {
    if (!d3Container.current) return;

    const svg = d3.select(d3Container.current),
      width = +svg.attr('width'),
      height = +svg.attr('height'),
      g = svg.append('g').attr('transform', 'translate(40,0)');

    const treeLayout = d3.tree<TreeNode>().size([height, width - 160]);
    const root = d3.hierarchy<TreeNode>(data);
    treeLayout(root);

    const link = g
        .selectAll('.link')
        .data(root.descendants().slice(1) as d3.HierarchyPointNode<TreeNode>[])  // Ensure data is cast correctly
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('fill', 'none')
        .attr('stroke', '#ccc')  // Set stroke color for the link
        .attr('stroke-width', 2)  // Set stroke width for the link
        .attr('d', d3.linkVertical<d3.HierarchyPointNode<TreeNode>, d3.HierarchyPointNode<TreeNode>>()
          .x(d => d.y)  // Set x coordinate for both source and target
          .y(d => d.x)  // Set y coordinate for both source and target
          .source(d => d.parent!)  // Return the full parent node object as the source
          .target(d => d)  // Return the current node as the target
        );

    const node = g
      .selectAll('.node')
      .data<d3.HierarchyPointNode<TreeNode>>(root.descendants() as d3.HierarchyPointNode<TreeNode>[]) // Cast to HierarchyPointNode
      .enter()
      .append('g')
      .attr('class', d => `node ${d.children ? 'node--internal' : 'node--leaf'}`)
      .attr('transform', d => `translate(${d.y},${d.x})`);

    node.append('circle').attr('r', 10);

    node
      .append('text')
      .attr('dy', '.35em')
      .attr('x', d => (d.children ? -13 : 13))
      .style('text-anchor', d => (d.children ? 'end' : 'start'))
      .text(d => d.data.name);

    // Add drag behavior
    const drag = d3
      .drag<SVGGElement, d3.HierarchyPointNode<TreeNode>>()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);

    node.call(drag);

    function dragstarted(this: SVGGElement, event: any, d: d3.HierarchyPointNode<TreeNode>) {
      d3.select(this).raise().classed('active', true);
    }

    function dragged(this: SVGGElement, event: any, d: d3.HierarchyPointNode<TreeNode>) {
        d3.select(this).attr('transform', `translate(${(d.y += event.dx)},${(d.x += event.dy)})`);
        updateLinks();
    }
      
    function dragended(this: SVGGElement, event: any, d: d3.HierarchyPointNode<TreeNode>) {
        d3.select(this).classed('active', false);
    }
    function updateLinks() {
      link.attr('d', d => {
        return `M${d.y},${d.x}C${(d.y + d.parent!.y) / 2},${d.x} ${(d.y + d.parent!.y) / 2},${d.parent!.x} ${d.parent!.y},${d.parent!.x}`;
      });
    }

    return () => {
      // Cleanup the chart if the component is unmounted
      svg.selectAll('*').remove();
    };
  }, []);

  return (
    <div>
      <svg ref={d3Container} width="960" height="600"></svg>
    </div>
  );
};

export default TreeGraph;