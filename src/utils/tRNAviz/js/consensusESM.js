// consensusESM.js
import * as d3 from 'd3';

/** 
 * 用于将 position => feature 短码
 */
const feature_code = {
  'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', 'Absent': '-', 'N': 'N',
  'Purine': 'R', 'Pyrimidine': 'Y', 'C / G': 'S', 'A / U': 'W', 'A / C': 'M', 'G / U': 'K',
  'C / G / U': 'B', 'A / C / U': 'H', 'A / G / U': 'D', 'A / C / G': 'V',
  'Paired': ':', 'Mismatched': '÷'
};

/** 
 * 某些特征对应的组合信息（在表格或判断时用）
 */
const provenance = {
  'A': ['A'], 'C': ['C'], 'G': ['G'], 'U': ['U'],
  'Purine': ['A', 'G', 'Purine'], 'Pyrimidine': ['C', 'U', 'Pyrimidine'],
  // ... 省略部分
  'A:U / C:G': ['A:U', 'C:G'],
  'G:C / U:A': ['G:C', 'U:A']
};

/** 
 * 颜色比例尺，将不同特征映射到固定颜色 
 */
const feature_scale = d3.scaleOrdinal()
  .domain([
    '', 'A', 'C', 'G', 'U', '-', 'Purine', 'Pyrimidine',
    'Weak', 'Strong', 'Amino', 'Keto', 'B', 'D', 'H', 'V', 'N',
    'Absent', 'Mismatched', 'Paired', 'High mismatch rate',
    'A / U', 'C / G', 'A / C', 'G / U', 'C / G / U', 'A / G / U', 'A / C / U', 'A / C / G',
    'A:U', 'U:A', 'G:C', 'C:G', 'G:U', 'U:G', 'A:G', 'G:A', 'C:U', 'U:C', 'A:C', 'C:A', 'A:A', 'C:C', 'G:G', 'U:U',
    'Malformed', 'A:-', '-:A', 'C:-', '-:C', 'G:-', '-:G', 'U:-', '-:U', '-:-'
  ])
  .range([
    '#ffffff', '#ffd92f', '#4daf4a', '#e41a1c', '#377eb8', '#7f7f7f', '#ff8300','#66c2a5','#b3de69','#fb72b2','#c1764a','#b26cbd',
    '#e5c494','#ccebd5','#ffa79d','#a6cdea','#ffffff','#7f7f7f','#333333','#ffffcc','#b3b3b3','#b3de69','#fb72b2','#c1764a','#b26cbd',
    '#e5c494','#ccebd5','#ffa79d','#a6cdea','#17b3cf','#9ed0e5','#ff7f0e','#ffbb78','#a067bc','#ceafd5','#2fc69e','#8be4cf','#e377c2',
    '#f7b6d2','#c47b70','#f0a994','#e7cb94','#cedb9c','#e7969c','#9ca8de','#333333','#333333','#333333','#333333','#333333','#333333',
    '#333333','#333333','#333333','#7f7f7f'
  ]);

/**
 * 绘制 Cloverleaf tRNA 结构的函数
 * @param {Object} cloverleaf_data - 键为 position (如 "1","73")，值为 { feature, datatype, freqs }
 * @param {String} isotype - 用于标识 isotype（只是附加在 highlight 时使用）
 * @param {String} coordsUrl - 指定一个 coords.json 的路径
 */
export function draw_cloverleaf(cloverleaf_data, isotype, coordsUrl) {
  // 宽高设置
  const cloverleaf_area_width = 525;
  const cloverleaf_area_height = 550;

  // 创建主 SVG
  const svgContainer = d3.select('#cloverleaf-area')
    .append('svg')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)
    .attr('class', 'cloverleaf-svg')
    .attr('id', 'cloverleaf');

  // 在 svg 内加一个 <g>
  const cloverleaf = svgContainer.append('g')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height);

  // 添加一个白色矩形占满 svg，用来监听点击，解锁 highlight
  svgContainer
    .append('rect')
    .attr('width', cloverleaf_area_width)
    .attr('height', cloverleaf_area_height)
    .attr('fill', 'white')
    .on('click', function() {
      if (d3.select('#cloverleaf').attr('locked')) {
        dehighlight();
        d3.select('#cloverleaf').attr('locked', null);
      }
    });

  // 在 body 上添加一个 tooltip
  d3.select('body')
    .append('div')
    .attr('class', 'tooltip tooltip-cloverleaf')
    .style('opacity', 0);

  // 用 d3.json 加载 coordsUrl（其中应该是 coords 数组：[{ position, x, y, radius }, ...]）
  d3.json(coordsUrl).then((coords) => {
    // 创建 circle
    cloverleaf.selectAll('circle')
      .data(coords, d => 'circle' + d.position)
      .enter()
      .append('circle')
      .attr('class', 'cloverleaf-circle')
      .attr('id', d => 'circle' + d.position)
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', d => d.radius);

    // 创建文字（用于显示特征）
    cloverleaf.selectAll('text')
      .data(coords, d => 'consensus' + d.position)
      .enter()
      .append('text');

    // coords 加载完后，才执行 update_cloverleaf
    update_cloverleaf(cloverleaf_data);
  })
  .catch(err => {
    console.error("[draw_cloverleaf] Error loading coords =>", err);
  });

  // 将 cloverleaf_data 的 feature, datatype, freqs 合并到 coords 里
  function update_cloverleaf(cloverleaf_data) {
    const coords = cloverleaf.selectAll('circle').data();
    coords.forEach(item => {
      const pos = item.position;
      if (cloverleaf_data[pos]) {
        item.feature  = cloverleaf_data[pos].feature;
        item.datatype = cloverleaf_data[pos].datatype;
        item.freqs    = cloverleaf_data[pos].freqs;
      } else {
        // 如果 cloverleaf_data 中没有对应 position，暂时标为空
        item.feature  = '';
        item.datatype = '';
        item.freqs    = {};
      }
    });
    set_cloverleaf_circle_attributes(coords);
    set_cloverleaf_text_attributes(coords);
  }

  // 设置 circle 的属性和事件
  function set_cloverleaf_circle_attributes(coords) {
    const tooltip = d3.select('.tooltip-cloverleaf');
    const tooltip_position = tooltip.append('div').attr('class', 'tooltip-position');
    const tooltip_consensus = tooltip.append('div').attr('class', 'tooltip-consensus');
    const tooltip_datatype = tooltip.append('div').attr('class', 'tooltip-datatype');

    cloverleaf.selectAll('circle')
      .data(coords)
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', d => d.radius)
      .classed('cloverleaf-near-consensus', d => d.datatype === 'Near-consensus')
      .attr('fill', d => feature_scale(d.feature))
      .on('mouseover', function(d) {
        if (!cloverleaf.attr('locked')) {
          dehighlight();
          highlight(d);
        }
      })
      .on('mousemove', function(d) {
        if (!cloverleaf.attr('locked')) {
          tooltip.style('left', d3.event.pageX + 'px')
                 .style('top', d3.event.pageY + 'px');
        }
      })
      .on('mouseout', (d) => {
        if (!cloverleaf.attr('locked')) {
          dehighlight();
        }
      })
      .on('click', function(d) {
        if (!cloverleaf.attr('locked')) {
          cloverleaf.attr('locked', true);
          tooltip.transition()
            .duration(100)
            .style('opacity', 0);
        } else {
          dehighlight();
          cloverleaf.attr('locked', null);
          highlight(d);
        }
      });
  }

  // hover 高亮
  function highlight(d) {
    d3.select('.tooltip-position').html('Position ' + d.position);
    if (d.feature) {
      d3.select('.tooltip-consensus').html(d.feature);
      d3.select('.tooltip-datatype').html(d.datatype);
    } else {
      d3.select('.tooltip-consensus').html('');
      d3.select('.tooltip-datatype').html('');
    }
    d3.select('.tooltip-cloverleaf').transition()
      .duration(100)
      .style('opacity', 0.95)
      .style('left', d3.event.pageX + 'px')
      .style('top', d3.event.pageY + 'px');

    d3.select('#circle' + d.position)
      .classed('cloverleaf-highlight', true);

    // 调用 base_distro
    update_base_distro(d, 'cloverleaf', isotype);
  }

  // hover 取消
  function dehighlight() {
    d3.select('.tooltip-cloverleaf').style('opacity', 0);
    d3.select('.cloverleaf-highlight')
      .classed('cloverleaf-highlight', false);
  }

  // 给 text 设置其属性
  function set_cloverleaf_text_attributes(coords) {
    cloverleaf.selectAll('text')
      .data(coords)
      .attr('id', d => 'consensus' + d.position)
      .attr('x', d => d.x)
      .attr('y', d => {
        // 如果 position 不含 'V'，就 y+5，否则 y+4
        return d.position.indexOf('V') === -1 ? (d.y + 5) : (d.y + 4);
      })
      .attr('opacity', d => d.datatype === 'Near-consensus' ? 0.3 : 1)
      .attr('text-anchor', 'middle')
      .attr('font-size', d => {
        return d.position.indexOf('V') === -1 ? '15px' : '10px';
      })
      .text(d => feature_code[d.feature] || '')
      .style('pointer-events', 'none');
  }
}

/**
 * 绘制“碱基分布”条形图
 * @param {Object} freq_data - 可能与 draw_cloverleaf 里的 freq_data 相同结构
 * @param {String} plot_type - 标识是 'cloverleaf' or 'tilemap'，以决定坐标刻度
 */
export function draw_base_distro(freq_data, plot_type) {
  const base_distro_area_width = 765,
        base_distro_area_height = 375,
        base_distro_width = 710,
        base_distro_height = 325;

  const base_distro = d3.select(`#${plot_type}-base-distro-area`)
    .append('svg')
    .attr('width', base_distro_area_width)
    .attr('height', base_distro_area_height)
    .attr('class', `${plot_type}-base-distro-svg`)
    .attr('id', `${plot_type}-base-distro`)
    .append('g')
    .attr('width', base_distro_area_width)
    .attr('height', base_distro_area_height);

  // 根据 plot_type 不同，先初始化 Y 轴
  if (plot_type === 'cloverleaf') {
    const max_freq = d3.max(
      Object.values(freq_data).map(d => d3.sum(Object.values(d.freqs)))
    );
    const base_freq_scale = d3.scaleLinear()
      .domain([0, max_freq])
      .range([base_distro_height, 0]);
    const base_freq_axis = d3.axisLeft(base_freq_scale);

    base_distro.append('g')
      .attr('id', `${plot_type}-base-yaxis`)
      .attr('class', 'base-yaxis')
      .attr('transform', 'translate(63, 10)')
      .call(base_freq_axis);

  } else {
    // 比如 tilemap / 其他情况
    const isotype_max_freq = d3.max(
      Object.values(freq_data).map(d => d3.sum(Object.values(d.freqs)))
    );
    const isotype_base_freq_scale = d3.scaleLinear()
      .domain([0, isotype_max_freq])
      .range([base_distro_height, 0]);
    const isotype_base_freq_axis = d3.axisLeft(isotype_base_freq_scale);

    base_distro.append('g')
      .attr('id', `${plot_type}-base-yaxis`)
      .attr('class', 'base-yaxis')
      .attr('transform', 'translate(70, 10)')
      .call(isotype_base_freq_axis);
  }

  const base_feature_scale = d3.scaleBand()
    .domain(['A', 'C', 'G', 'U', 'Absent'])
    .range([0, base_distro_width / 2])
    .paddingInner(0.2);

  const base_feature_axis = d3.axisBottom(base_feature_scale);
  base_distro.append('g')
    .attr('id', `${plot_type}-base-xaxis`)
    .attr('class', 'base-xaxis')
    .attr('transform', `translate(70, ${base_distro_height + 15})`)
    .call(base_feature_axis);

  base_distro.selectAll('.base-xaxis .tick text, .base-yaxis .tick text')
    .attr('class', 'axis-text');

  // 在后面 update_base_distro 中还会细化
}

// 在 highlight 里会调用此函数
let update_base_distro = () => { /* 占位：在 draw_cloverleaf 里赋值 */ };

/**
 * 在 draw_cloverleaf() highlight 时调用的更新函数
 * 下面是实际定义 / 覆盖
 */
update_base_distro = (coord, plot_type, isotype) => {
  const base_distro_width = 700,
        base_distro_height = 325;

  const base_distro = d3.select(`#${plot_type}-base-distro`);

  // 清理旧的 axis 与 rect
  base_distro.selectAll('g.base-xaxis, g.base-yaxis, g.rects').remove();

  // 计算 X 轴特征列表
  const current_features = Object.keys(coord.freqs).sort((a, b) => {
    if (a === 'Absent') return 1;
    if (b === 'Absent') return -1;
    return a < b ? -1 : 1;
  });
  const base_feature_scale = d3.scaleBand()
    .domain(current_features)
    .range([0, current_features.length > 10 ? base_distro_width - 10 : base_distro_width / 2])
    .paddingInner(0.2);

  const base_feature_axis = d3.axisBottom(base_feature_scale);
  base_distro.append('g')
    .attr('id', `${plot_type}-base-xaxis`)
    .attr('class', 'base-xaxis')
    .attr('transform', `translate(70, ${base_distro_height + 15})`)
    .call(base_feature_axis);

  // Y 轴：如果是 tilemap，就可能对 isotype 做聚合；否则直接看当前 coord
  let base_freq_scale;
  if (plot_type === 'tilemap') {
    // 这里 freq_data 也要取全局
    // 但为了简化，直接自定义
  } else {
    const max_freq = d3.sum(Object.values(coord.freqs));
    base_freq_scale = d3.scaleLinear()
      .domain([0, max_freq])
      .range([base_distro_height, 0]);
  }
  const base_freq_axis = d3.axisLeft(base_freq_scale);

  const base_yaxis = base_distro.append('g')
    .attr('class', 'base-yaxis')
    .attr('id', `${plot_type}-base-yaxis`)
    .attr('transform', 'translate(63, 10)')
    .call(base_freq_axis);

  base_yaxis.append('g')
    .attr('transform', 'translate(-63, -20)')
    .append('text')
    .attr('class', 'yaxis-label')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0)
    .attr('x', 0 - (base_distro_area_height / 2))
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .text('Counts');

  base_distro.selectAll('.base-xaxis .tick text, .base-yaxis .tick text')
    .attr('class', 'axis-text');

  // 绘制矩形
  const rectGroup = base_distro.append('g')
    .attr('class', 'rects')
    .attr('transform', 'translate(70, 10)');

  rectGroup.selectAll('rect')
    .data(d3.entries(coord.freqs))
    .enter()
    .append('rect')
    .attr('x', d => base_feature_scale(d.key))
    .attr('y', d => base_freq_scale(d.value))
    .attr('id', d => `cloverleaf-rect-${d.key.replace(':','-')}-${d.value}`)
    .attr('height', d => base_distro_height - base_freq_scale(d.value))
    .attr('width', base_feature_scale.bandwidth())
    .attr('stroke', '#666666')
    .attr('stroke-width', '1')
    .style('fill', d => feature_scale(d.key))
    .style('fill-opacity', 0.7);
};