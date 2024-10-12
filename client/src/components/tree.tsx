import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface TreeNode {
  name: string;
  children?: TreeNode[];
}

const TreeGraph: React.FC = () => {
  const d3Container = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (d3Container.current) {
      const data: TreeNode = {
        name: "Machine Learning",
        children: [
          {
            name: "Supervised Learning",
            children: [
              { name: "Classification" },
              { name: "Regression" },
              { name: "Neural Networks" }
            ]
          },
          {
            name: "Unsupervised Learning",
            children: [
              { name: "Clustering" },
              { name: "Dimensionality Reduction" },
              { name: "Anomaly Detection" }
            ]
          },
          {
            name: "Reinforcement Learning",
            children: [
              { name: "Q-Learning" },
              { name: "Policy Gradients" },
              { name: "Deep Q-Networks" }
            ]
          },
          {
            name: "Deep Learning",
            children: [
              { name: "CNNs" },
              { name: "RNNs" },
              { name: "Transformers" }
            ]
          },
          {
            name: "Model Evaluation",
            children: [
              { name: "Cross-Validation" },
              { name: "Metrics" },
              { name: "Overfitting/Underfitting" }
            ]
          }
        ]
      };

      // Set the dimensions and margins for the graph
      const margin = { top: 20, right: 120, bottom: 20, left: 120 };
      const width = 300 - margin.left - margin.right; // Adjust the width as needed
      const height = 300 - margin.top - margin.bottom; // Adjust the height as needed

      // Clear the container if it already has elements
      d3.select(d3Container.current).selectAll("*").remove();

      const svg = d3
        .select(d3Container.current)
        .append("svg")
        .attr("width", "100%") // Make SVG responsive to its container's width
        .attr("height", "100%") // Make SVG responsive to its container's height
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`) 
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Create a tree layout
      const treeLayout = d3.tree<TreeNode>().size([height, width]);

      // Create the root node
      const root = d3.hierarchy(data);

      // Generate the tree layout
      treeLayout(root);

      // Links (paths connecting the nodes)
      const linkGenerator = d3.linkHorizontal<d3.HierarchyPointLink<TreeNode>, d3.HierarchyPointNode<TreeNode>>()
        .x(d => d.y)
        .y(d => d.x);

      svg
        .selectAll('path.link')
        .data(root.links())
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('fill', 'none')
        .attr('stroke', '#ccc')
        .attr('stroke-width', 2)
        .attr('d', d => linkGenerator(d as d3.HierarchyPointLink<TreeNode>));

      // Node generation remains the same
      const node = svg
        .selectAll('g.node')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.y},${d.x})`);

      node
        .append('circle')
        .attr('r', 5)
        .attr('fill', 'steelblue');

      node
        .append('text')
        .attr('dy', '.35em')
        .attr('x', d => d.children ? -13 : 13)
        .attr('text-anchor', d => d.children ? 'end' : 'start')
        .text(d => d.data.name);
    }
  }, []);

  return (
    <div className="tree-graph w-full h-full">
      <svg ref={d3Container}></svg>
    </div>
  );
};

export default TreeGraph;