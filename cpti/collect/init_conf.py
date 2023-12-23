# 数据处理
def neb_interpolate(args):
    # 通过ase.io读取始末结构。
    from ase import io
    # 只有一个轨迹文件的情形。
    if len(args.images) == 1:
        images = io.iread(args.images[0])
        images = list(images)
        initial = images[0]
        final = images[-1]
    # 使用两个结构的情形。
    elif len(args.images) == 2:
        initial = io.read(args.images[0])
        final = io.read(args.images[-1])
    else:
        initial = None
        final = None
        exit('Number of images must be a trajactory or two structures.')
    # 初始化路径，共nimage个结构。
    images = [initial]+[initial.copy() for i in range(args.nimage-2)]+[final]
    # 将多帧images转换为NEB对象。
    from ase.neb import NEB
    neb = NEB(images, k=args.spring)
    # 可以按照https://wiki.fysik.dtu.dk/ase/ase/neb.html，最终NEB中的image将被更新。
    if args.method == 'linear':
        neb.interpolate(method='linear')
    elif args.method == 'idpp':
        neb.interpolate()
        # 可选优化算法。
        from ase.optimize import MDMin, BFGS, LBFGS, FIRE
        index = {'MDMin': MDMin, 'BFGS': BFGS, 'LBFGS': LBFGS, 'FIRE': FIRE}
        neb.idpp_interpolate(
            fmax=args.fmax, optimizer=index[args.optimizer], steps=args.nstep)
    return images

# 输出结果
def write_guess(args, images):
    # 按编号建立文件夹，没文件夹的建文件夹，有文件夹的跳过。
    import os
    [os.mkdir('%02d' % i)
     for i in range(len(images)) if not os.path.exists('%02d' % i)]
    # 到对应目录去写入POSCAR文件。
    from ase import io
    [io.write('%02d/POSCAR' % i, images[i]) for i in range(len(images))]
    # 如果需要写入XDATCAR。
    if args.output:
        io.write('XDATCAR', images)
    # 如果需要导入MS可以使用，可以手动运行ase convert XDATCAR name.xtd进行转换。
    # XDATCAR也可以通过ase gui XDATCAR来进行预览。
# 主程序
def init_conf(args):
    pass
    #p = parse_args()
    #args = p.parse_args()
    # 若处理失败则显示菜单
    try:
        # 数据处理
        images = neb_interpolate(args)
        # 输出结果
        write_guess(args, images)
    except:
        p.print_help()